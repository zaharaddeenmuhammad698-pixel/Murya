from flask import Flask, request, render_template_string, Response
import json, os, csv, io
from datetime import datetime

app = Flask(__name__)
REPORTS_FILE = "reports.json"

# SAFE - No crash if key missing
AT_USERNAME = os.environ.get("AT_USERNAME")
AT_API_KEY = os.environ.get("AT_API_KEY")

# Only init Africa's Talking if keys exist - prevents crash
sms = None
if AT_USERNAME and AT_API_KEY:
    try:
        import africastalking
        africastalking.initialize(AT_USERNAME, AT_API_KEY)
        sms = africastalking.SMS
        print(f"✅ AT initialized as {AT_USERNAME}")
    except Exception as e:
        print(f"⚠️ AT init failed: {e}")
        sms = None
else:
    print("⚠️ No AT keys in Environment - USSD will work, SMS reply will need keys")

if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE,'w') as f: json.dump([], f)

def save_report(phone, pu, issue_type, details, lang):
    try:
        with open(REPORTS_FILE,'r') as f: data=json.load(f)
    except: data=[]
    data.append({"phone":phone,"pu":pu,"issue_type":issue_type,"issue":details,"language":lang,"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    with open(REPORTS_FILE,'w') as f: json.dump(data,f,indent=2)

DASHBOARD_HTML = """<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MURYAN ZABE</title>
<style>body{font-family:Arial;background:#f5f5f5;padding:10px}.card{background:white;padding:15px;border-radius:12px;margin-bottom:15px}
h1{color:#0a7e07}table{width:100%;border-collapse:collapse;font-size:11px}th{background:#0a7e07;color:white;padding:6px}td{padding:6px;border-bottom:1px solid #ddd}
.btn{background:#0a7e07;color:white;padding:8px 12px;border-radius:8px;border:none}input{padding:8px;width:60%;border:1px solid #ccc;border-radius:8px}</style></head><body>
<div class="card"><h1>🇳🇬 MURYAN ZABE - Bauchi</h1><p>{{count}} Reports | Sender: MURYA | <a href="/export">Export CSV</a><br>
{% if not sms_ready %}<span style="color:red">⚠️ SMS not ready - Add AT keys in Render Environment</span>{% else %}<span style="color:green">✅ SMS Ready as MURYA</span>{% endif %}</p></div>
<div class="card" style="overflow-x:auto"><table><tr><th>Time</th><th>Phone</th><th>PU</th><th>Type</th><th>Details</th><th>Reply</th></tr>
{% for r in reports[::-1] %}<tr><td>{{r.time}}</td><td>{{r.phone}}</td><td>{{r.pu}}</td><td>{{r.issue_type}}</td><td>{{r.issue}}</td>
<td><form action="/reply" method="post"><input type="hidden" name="phone" value="{{r.phone}}"><input type="text" name="message" placeholder="Mun karbi..." required>
<button class="btn" type="submit">📩 MURYA</button></form></td></tr>{% endfor %}</table></div></body></html>"""

@app.route('/murya', methods=['POST'])
def ussd():
    phone=request.values.get("phoneNumber"); text=request.values.get("text",""); parts=text.split("*")
    if text=="": return "CON MURYAN ZABE - Bauchi\n1. English\n2. Hausa"
    if len(parts)==1: return "CON Enter PU Code:\n(e.g. 05-04-02-001)" if parts[0]=="1" else "CON Lambar Akwatin Zabe:\n(misali 05-04-02-001)"
    if len(parts)==2:
        if parts[0]=="1": return "CON Select Issue:\n1. BVAS Failure\n2. Late Materials\n3. Vote Buying\n4. Violence\n5. No EC8A\n6. Other"
        else: return "CON Zabi Matsala:\n1. BVAS lalace\n2. Kayan sun makara\n3. Sayen kuri'a\n4. Tashin hankali\n5. Babu EC8A\n6. Sauran"
    if len(parts)==3: return "CON Describe:" if parts[0]=="1" else "CON Bayyana:"
    if len(parts)==4:
        lang="English" if parts[0]=="1" else "Hausa"
        pu=parts[1]; issue_type=parts[2]; details=parts[3]
        save_report(phone, pu, issue_type, details, lang)
        return "END Thanks! Report received. PU:"+pu if lang=="English" else "END Nagode! Mun karbi. PU:"+pu
    return "END Error"

@app.route('/reply', methods=['POST'])
def reply_sms():
    phone=request.form.get("phone"); message=request.form.get("message")
    if not sms:
        return f"<h2>⚠️ SMS not configured</h2><p>Add AT_USERNAME and AT_API_KEY in Render Environment, then Save & Deploy.</p><p>Current: USER={AT_USERNAME} KEY set={bool(AT_API_KEY)}</p><a href='/dashboard'>Back</a>"
    try:
        sms.send(message, [phone], sender_id="MURYA")
        return f"<h2>✅ Sent as MURYA to {phone}</h2><p>{message}</p><a href='/dashboard'>Back</a>"
    except Exception as e:
        return f"<h2>❌ {e}</h2><p>Check keys & funds</p><a href='/dashboard'>Back</a>"

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
    return render_template_string(DASHBOARD_HTML, reports=data, count=len(data), sms_ready=bool(sms))

if __name__=='__main__': app.run(host='0.0.0.0', port=10000)