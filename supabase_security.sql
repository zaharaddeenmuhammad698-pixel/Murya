-- MURYA on Supabase: lock the tables so the public API key can never read them.
-- Run this ONCE in the Supabase SQL editor, AFTER the tables exist (open the app once, or run the migration script).
-- Your app connects directly with the database password, which is not affected by these rules.

alter table if exists public.questions      enable row level security;
alter table if exists public.kb             enable row level security;
alter table if exists public.polling_units  enable row level security;
alter table if exists public.pu_meta        enable row level security;
alter table if exists public.audit_log      enable row level security;
alter table if exists public.login_attempts enable row level security;
alter table if exists public.reports        enable row level security;

revoke all on all tables    in schema public from anon, authenticated;
revoke all on all sequences in schema public from anon, authenticated;
alter default privileges in schema public revoke all on tables    from anon, authenticated;
alter default privileges in schema public revoke all on sequences from anon, authenticated;

-- Check: every table should show rowsecurity = true.
select tablename, rowsecurity from pg_tables where schemaname = 'public' order by tablename;
