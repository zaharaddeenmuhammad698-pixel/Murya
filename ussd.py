from flask import Flask, request, render_template_string, Response
import json, os, csv, io
from datetime import datetime
import africastalking

app = Flask(__name__)
REPORTS_FILE = "reports.json"

# YOUR SANDBOX KEYS - FINAL
AT_USERNAME = "sandbox"
AT_API_KEY = "atsk_a65322902d2ecbf0e946719d64c94a15779a46462c9b0c9d1e723acfb9fefb90dca78573"

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE,'w') as f: json.dump([], f)

def save_report(phone, text, lang):
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    report={"phone":phone,"issue":text,"language":lang,"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    data.append(report)
    with open(REPORTS_FILE,'w') as f: json.dump(data,f,indent=2)

DASHBOARD_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYA - Official</title>
<style>body{font-family:Arial;background:#f5f5f5;padding:10px}.card{background:white;padding:15px;border-radius:12px;margin-bottom:15px}
h1{color:#0a7e07}table{width:100%;border-collapse:collapse;font-size:12px}th{background:#0a7e07;color:white;padding:8px}
td{padding:8px;border-bottom:1px solid #ddd}.btn{color:white;padding:8px 12px;border-radius:8px;border:none}
.btn-send{background:#0a7e07}input{padding:8px;width:70%;border:1px solid #ccc;border-radius:8px}
.status{color:#0a7e07;font-weight:bold}</style></head><body>
<div class="card"><h1>🇳🇬 MURYA - Official Sender: MURYA</h1><p>{{count}} Reports | Cost ~₦4/SMS | <a href="/export">Export CSV</a></p>
<p class="status">✅ Citizens will see sender as: MURYA (no contact saving needed)</p></div>
<div class="card" style="overflow-x:auto"><table>
<tr><th>Time</th><th>Phone</th><th>Issue</th><th>Reply as MURYA</th></tr>
{% for r in reports[::-1] %}<tr><td>{{r.time}}</td><td>{{r.phone}}</td><td>{{r.issue}}</td>
<td><form action="/reply" method="post"><input type="hidden" name="phone" value="{{r.phone}}">
<input type="text" name="message" placeholder="Reply e.g. Mun karbi..." required>
<button class="btn btn-send" type="submit">📩 Send as MURYA</button></form></td></tr>{% endfor %}
</table></div></body></html>
"""

@app.route('/murya', methods=['POST'])
def ussd():
    phone=request.values.get("phoneNumber"); text=request.values.get("text",""); parts=text.split("*")
    if text=="": return "CON MURYA\n1. English\n2. Hausa"
    if len(parts)==1: return "CON Choose:\n1. Water\n2. Road\n3. Light\n4. Other" if parts[0]=="1" else "CON Zabi:\n1. Ruwa\n2. Hanya\n3. Wuta\n4. Sauran" if parts[0]=="2" else "END Invalid"
    if len(parts)==2: return "CON Describe:\n" if parts[0]=="1" else "CON Bayyana:\n"
    if len(parts)==3:
        lang="English" if parts[0]=="1" else "Hausa"; save_report(phone, f"{parts[1]}: {parts[2]}", lang)
        return "END Thanks! Report received." if lang=="English" else "END Nagode! Mun karbi."
    return "END Error"

@app.route('/reply', methods=['POST'])
def reply_sms():
    phone=request.form.get("phone"); message=request.form.get("message")
    try:
        sms.send(message, [phone], sender_id="MURYA")
        return f"<h2>✅ Sent as MURYA to {phone}</h2><p>{message}</p><a href='/dashboard'>Back</a>"
    except Exception as e:
        return f"<h2>❌ {e}</h2><p>Fund account & approve MURYA ID first</p><a href='/dashboard'>Back</a>"

@app.route('/export')
def export_csv():
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    si=io.StringIO(); cw=csv.writer(si); cw.writerow(['time','phone','language','issue'])
    for r in data: cw.writerow([r['time'],r['phone'],r['language'],r['issue']])
    return Response(si.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=murya.csv"})

@app.route('/dashboard')
@app.route('/')
def dashboard():
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    return render_template_string(DASHBOARD_HTML, reports=data, count=len(data))

if __name__=='__main__': app.run(host='0.0.0.0', port=10000)