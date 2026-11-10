"""
pgcompat.py: lets MURYA's SQLite-style database code run on Postgres (Supabase). Optional.

How it is used: app.py (and ussd.py) call  pgcompat.connect(DATABASE_URL)  only when a DATABASE_URL secret is set.
Without that secret nothing here is loaded and MURYA keeps using its local SQLite file.

What it does, so the rest of the code does not change:
  - turns ? placeholders into %s,
  - turns  INSERT OR REPLACE  into  INSERT ... ON CONFLICT ... DO UPDATE,
  - turns  INTEGER PRIMARY KEY AUTOINCREMENT  into  SERIAL PRIMARY KEY,  REAL into DOUBLE PRECISION,  LIKE into ILIKE,
  - answers  PRAGMA table_info(t)  from information_schema, and ignores other PRAGMA lines,
  - gives  cursor.lastrowid  after an INSERT (using RETURNING id),
  - keeps a small pool of connections (opening a new one for every query would be slow),
  - retries once if the very first statement of a block finds the connection was closed.
Needs:  pip install psycopg2-binary
"""
import re
import threading

SERIAL_TABLES = {"questions", "kb", "audit_log", "polling_units", "reports"}   # tables with an id column
CONFLICT_KEYS = {"pu_meta": "k", "settings": "k"}                              # tables written with INSERT OR REPLACE

_driver = None          # tests can put a fake driver here
_pool = None
_pool_url = None
_lock = threading.Lock()


def translate(sql):
    """Return Postgres SQL for a SQLite-style statement, or None for statements that Postgres does not need."""
    s = sql.strip().rstrip(";")
    m = re.match(r"PRAGMA\s+table_info\s*\(\s*(\w+)\s*\)", s, re.I)
    if m:
        return ("SELECT column_name AS name FROM information_schema.columns "
                "WHERE table_schema = current_schema() AND table_name = '%s'" % m.group(1).lower())
    if re.match(r"PRAGMA\b", s, re.I):
        return None
    m = re.match(r"INSERT\s+OR\s+REPLACE\s+INTO\s+(\w+)\s*\(([^)]*)\)\s*VALUES\s*\((.*)\)\s*$", s, re.I | re.S)
    if m:
        table, cols, vals = m.group(1).lower(), m.group(2), m.group(3)
        if table not in CONFLICT_KEYS:
            raise ValueError(f"pgcompat: INSERT OR REPLACE is not set up for table {table}")
        key = CONFLICT_KEYS[table]
        sets = ", ".join(f"{c.strip()} = EXCLUDED.{c.strip()}" for c in cols.split(",") if c.strip() != key)
        s = f"INSERT INTO {table}({cols}) VALUES ({vals}) ON CONFLICT ({key}) DO UPDATE SET {sets}"
    s = re.sub(r"INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT", "SERIAL PRIMARY KEY", s, flags=re.I)
    s = re.sub(r"\bREAL\b", "DOUBLE PRECISION", s)
    s = re.sub(r"(?<![A-Za-z])LIKE(?![A-Za-z])", "ILIKE", s)     # SQLite's LIKE ignores case, Postgres's does not
    return s.replace("%", "%%").replace("?", "%s")


def _load_driver():
    global _driver
    if _driver is None:
        import psycopg2
        import psycopg2.extras
        import psycopg2.pool
        _driver = psycopg2
    return _driver


def _with_ssl(url):
    return url if "sslmode=" in url else url + ("&" if "?" in url else "?") + "sslmode=require"


def _get_pool(url):
    global _pool, _pool_url
    with _lock:
        if _pool is None or _pool_url != url:
            drv = _load_driver()
            _pool = drv.pool.ThreadedConnectionPool(1, 4, _with_ssl(url), cursor_factory=drv.extras.DictCursor, connect_timeout=10)
            _pool_url = url
        return _pool


class PgCursor:
    def __init__(self, conn):
        self._conn = conn
        self._cur = None
        self.lastrowid = None
        self.rowcount = -1

    def _open(self):
        self._cur = self._conn._raw.cursor()

    def _run(self, sql, params, many=False):
        drv = _load_driver()
        first = self._conn._n_exec == 0
        self._conn._n_exec += 1
        for attempt in (0, 1):
            try:
                self._open()
                if many: self._cur.executemany(sql, params)
                else: self._cur.execute(sql, params)
                self.rowcount = self._cur.rowcount
                return
            except (drv.OperationalError, drv.InterfaceError):
                if attempt or not first: raise        # only the first statement of a block can be retried safely
                self._conn._replace_raw()

    def execute(self, sql, params=()):
        t = translate(sql)
        if t is None:
            return self
        m = re.match(r"\s*INSERT\s+INTO\s+(\w+)", t, re.I)
        returning = bool(m and m.group(1).lower() in SERIAL_TABLES and "RETURNING" not in t.upper())
        if returning: t += " RETURNING id"
        self._run(t, params if isinstance(params, dict) else tuple(params))
        if returning:
            row = self._cur.fetchone()
            self.lastrowid = row[0] if row else None
        return self

    def executemany(self, sql, seq):
        t = translate(sql)
        if t is not None: self._run(t, [tuple(p) for p in seq], many=True)
        return self

    def fetchone(self):
        return self._cur.fetchone() if self._cur is not None else None

    def fetchall(self):
        return self._cur.fetchall() if self._cur is not None else []

    def __iter__(self):
        return iter(self.fetchall())


class PgConnection:
    """Works like the sqlite3 connection the rest of the code expects:  with connect(url) as c: c.execute(...)."""
    def __init__(self, pool, url):
        self._pool, self._url = pool, url
        self._raw, self._pooled, self._n_exec = None, True, 0

    def _acquire(self):
        drv = _load_driver()
        try:
            raw = self._pool.getconn(); self._pooled = True
        except drv.pool.PoolError:                  # every pooled connection is busy: use a temporary one
            raw = drv.connect(_with_ssl(self._url), cursor_factory=drv.extras.DictCursor, connect_timeout=10); self._pooled = False
        if getattr(raw, "closed", 0):
            self._discard(raw)
            raw = drv.connect(_with_ssl(self._url), cursor_factory=drv.extras.DictCursor, connect_timeout=10); self._pooled = False
        self._raw = raw

    def _discard(self, raw):
        try:
            if self._pooled: self._pool.putconn(raw, close=True)
            else: raw.close()
        except Exception:
            pass

    def _replace_raw(self):
        self._discard(self._raw)
        self._acquire()

    def _release(self, ok):
        raw, self._raw = self._raw, None
        if raw is None: return
        try:
            raw.commit() if ok else raw.rollback()
        except Exception:
            ok = False
        if self._pooled: self._pool.putconn(raw, close=not ok and getattr(raw, "closed", 0) != 0)
        else: raw.close()

    def execute(self, sql, params=()):
        if self._raw is None: self._acquire()
        return PgCursor(self).execute(sql, params)

    def executemany(self, sql, seq):
        if self._raw is None: self._acquire()
        return PgCursor(self).executemany(sql, seq)

    def __enter__(self):
        self._n_exec = 0
        self._acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._release(exc_type is None)
        return False


def connect(url):
    return PgConnection(_get_pool(url), url)
