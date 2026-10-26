from flask import Flask, request, render_template_string, Response
import json, os, csv, io
from datetime import datetime
import africastalking

app = Flask(__name__)
REPORTS_FILE = "reports.json"

# USE ENVIRONMENT VARIABLES - SAFE!
AT_USERNAME = os.environ.get("AT_USERNAME", "sandbox")
AT_API_KEY = os.environ.get("AT_API_KEY", "sandbox")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE,'w') as f: json.dump([], f)

def save_report(phone, pu, issue_type, details, lang):
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    report={
        "phone":phone,
        "pu":pu,
        "issue_type":issue_type,
        "issue":details,
        "language":lang,
        "time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data.append(report)
    with open(REPORTS_FILE,'w') as f: json.dump(data,f,indent=2)

DASHBOARD_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYAN ZABE - Bauchi</title>
<style>body{font-family:Arial;background:#f5f5f5;padding:10px}.card{background:white;padding:15px;border-radius:12px;margin-bottom:15px}
h1{color:#0a7e07}table{width:100%;border-collapse:collapse;font-size:11px}th{background:#0a7e07;color:white;padding:6px}
td{padding:6px;border-bottom:1px solid #ddd}.btn{color:white;padding:8px 12px;border-radius:8px;border:none}
.btn-send{background:#0a7e07}input{padding:8px;width:60%;border:1px solid #ccc;border-radius:8px}</style></head><body>
<div class="card"><h1>🇳🇬 MURYAN ZABE - Bauchi Elections</h1><p>{{count}} Reports | Sender: MURYA | <a href="/export">Export CSV</a></p></div>
<div class="card" style="overflow-x:auto"><table>
<tr><th>Time</th><th>Phone</th><th>PU Code</th><th>Type</th><th>Details</th><th>Reply as MURYA</th></tr>
{% for r in reports[::-1] %}<tr><td>{{r.time}}</td><td>{{r.phone}}</td><td>{{r.pu}}</td><td>{{r.issue_type}}</td><td>{{r.issue}}</td>
<td><form action="/reply" method="post"><input type="hidden" name="phone" value="{{r.phone}}">
<input type="text" name="message" placeholder="Mun karbi rahoto..." required>
<button class="btn btn-send" type="submit">📩 MURYA</button></form></td></tr>{% endfor %}
</table></div></body></html>
"""

@app.route('/murya', methods=['POST'])
def ussd():
    phone=request.values.get("phoneNumber")
    text=request.values.get("text","")
    parts=text.split("*")

    # STEP 0 - Language
    if text=="":
        return "CON MURYAN ZABE - Bauchi\n1. English\n2. Hausa"

    # STEP 1 - Polling Unit
    if len(parts)==1:
        if parts[0]=="1":
            return "CON Enter Polling Unit Code:\n(e.g. 05-04-02-001)"
        else:
            return "CON Shigar da Lambar Akwatin Zabe:\n(misali 05-04-02-001)"

    # STEP 2 - Issue Type - REAL ELECTION QUESTIONS
    if len(parts)==2:
        if parts[0]=="1": # English
            return "CON Select Issue:\n1. BVAS Failure\n2. Late Materials\n3. Vote Buying\n4. Violence/Threat\n5. No Result Sheet\n6. Other"
        else: # Hausa
            return "CON Zabi Matsala:\n1. BVAS ya lalace\n2. Kayan zabe sun makara\n3. Sayen kuri'a\n4. Tashin hankali\n5. Babu Form EC8A\n6. Sauran"

    # STEP 3 - Describe
    if len(parts)==3:
        if parts[0]=="1":
            return "CON Describe situation:"
        else:
            return "CON Bayyana abin da ya faru:"

    # STEP 4 - Save
    if len(parts)==4:
        lang="English" if parts[0]=="1" else "Hausa"
        pu = parts[1]
        issue_map_en = {"1":"BVAS Failure","2":"Late Materials","3":"Vote Buying","4":"Violence","5":"No Result Sheet","6":"Other"}
        issue_map_ha = {"1":"BVAS lalace","2":"Kayan sun makara","3":"Sayen kuri'a","4":"Tashin hankali","5":"Babu EC8A","6":"Sauran"}
        issue_type = issue_map_en.get(parts[2], parts[2]) if lang=="English" else issue_map_ha.get(parts[2], parts[2])
        details = parts[3]
        save_report(phone, pu, issue_type, details, lang)
        if lang=="English":
            return "END Nagode! Report received.\nPU: "+pu+"\nWe will verify. Thank you!"
        else:
            return "END Nagode! Mun karbi rahoton.\nPU: "+pu+"\nZamu tabbatar. Mun gode!"

    return "END Error - Try again"

@app.route('/reply', methods=['POST'])
def reply_sms():
    phone=request.form.get("phone"); message=request.form.get("message")
    try:
        sms.send(message, [phone], sender_id="MURYA")
        return f"<h2>✅ Sent as MURYA to {phone}</h2><p>{message}</p><a href='/dashboard'>Back</a>"
    except Exception as e:
        return f"<h2>❌ {e}</h2><p>Check funds & MURYA approval</p><a href='/dashboard'>Back</a>"

@app.route('/export')
def export_csv():
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    si=io.StringIO(); cw=csv.writer(si); cw.writerow(['time','phone','pu','issue_type','issue','language'])
    for r in data: cw.writerow([r['time'],r['phone'],r['pu'],r['issue_type'],r['issue'],r['language']])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=muryan_zabe.csv"})

@app.route('/dashboard')
@app.route('/')
def dashboard():
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    return render_template_string(DASHBOARD_HTML, reports=data, count=len(data))

if __name__=='__main__': app.run(host='0.0.0.0', port=10000)