from flask import Flask, request, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)
REPORTS_FILE = "reports.json"

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'w') as f:
        json.dump([], f)

def save_report(phone, text, lang):
    try:
        with open(REPORTS_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = []
    data.append({
        "phone": phone,
        "issue": text,
        "language": lang,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open(REPORTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYA Dashboard</title>
<style>
body{font-family:Arial;background:#f5f5f5;padding:10px}
.card{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:15px}
h1{color:#0a7e07}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:#0a7e07;color:white;padding:10px;text-align:left}
td{padding:10px;border-bottom:1px solid #ddd}
.badge{padding:4px 8px;border-radius:8px;color:white;font-size:12px}
.hausa{background:#ff9800}
.english{background:#2196f3}
.count{font-size:32px;font-weight:bold;color:#0a7e07}
</style>
</head>
<body>
<div class="card">
<h1>🇳🇬 MURYA - Murya Jama'a</h1>
<p>Live Citizen Reports from *384*13833#</p>
<div class="count">{{count}} Reports</div>
<p><a href="/reports">JSON API</a> | <a href="/dashboard">Refresh</a></p>
</div>
<div class="card">
<table>
<tr><th>Time</th><th>Phone</th><th>Language</th><th>Issue</th></tr>
{% for r in reports[::-1] %}
<tr>
<td>{{r.time}}</td>
<td>{{r.phone}}</td>
<td><span class="badge {{r.language.lower()}}">{{r.language}}</span></td>
<td>{{r.issue}}</td>
</tr>
{% endfor %}
</table>
{% if count==0 %}<p>No reports yet. Dial *384*13833# to test</p>{% endif %}
</div>
</body>
</html>
"""

@app.route('/murya', methods=['POST'])
def ussd():
    phone = request.values.get("phoneNumber")
    text = request.values.get("text", "")
    parts = text.split("*")
    if text == "":
        return "CON Welcome to MURYA - Murya Jama'a\n1. English\n2. Hausa"
    if len(parts) == 1:
        if parts[0] == "1":
            return "CON Choose issue:\n1. Water\n2. Road\n3. Electricity\n4. Other"
        elif parts[0] == "2":
            return "CON Zabi matsala:\n1. Ruwa\n2. Hanya\n3. Wuta\n4. Sauran"
    if len(parts) == 2:
        return "CON Describe the issue:\n" if parts[0]=="1" else "CON Bayyana matsalar:\n"
    if len(parts) == 3:
        lang = "English" if parts[0]=="1" else "Hausa"
        save_report(phone, f"Type:{parts[1]} - {parts[2]}", lang)
        return "END Thank you! We received your report." if lang=="English" else "END Nagode! Mun karbi sako."
    return "END Error"

@app.route('/reports')
def reports():
    try:
        with open(REPORTS_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = []
    return {"count": len(data), "reports": data}

@app.route('/dashboard')
@app.route('/')
def dashboard():
    try:
        with open(REPORTS_FILE, 'r') as f:
            data = json.load(f)
    except:
        data = []
    return render_template_string(DASHBOARD_HTML, reports=data, count=len(data))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)