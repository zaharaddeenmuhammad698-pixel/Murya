from flask import Flask, request
import json
import os
from datetime import datetime

app = Flask(__name__)

REPORTS_FILE = "reports.json"

# Make file if not exist
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

@app.route('/murya', methods=['POST'])
def ussd():
    session_id = request.values.get("sessionId")
    phone = request.values.get("phoneNumber")
    text = request.values.get("text", "")
    
    # Split by *
    parts = text.split("*")
    
    # MENU 1: Welcome
    if text == "":
        response = "CON Welcome to MURYA - Murya Jama'a\n"
        response += "1. English\n"
        response += "2. Hausa"
        return response
    
    # MENU 2: Language selected
    if len(parts) == 1:
        if parts[0] == "1":
            response = "CON Choose issue:\n"
            response += "1. Water\n"
            response += "2. Road\n"
            response += "3. Electricity\n"
            response += "4. Other"
            return response
        elif parts[0] == "2":
            response = "CON Zabi matsala:\n"
            response += "1. Ruwa\n"
            response += "2. Hanya\n"
            response += "3. Wuta\n"
            response += "4. Sauran"
            return response
    
    # MENU 3: Issue type selected -> ask for description
    if len(parts) == 2:
        if parts[0] == "1":
            response = "CON Describe the issue:\n"
            return response
        else:
            response = "CON Bayyana matsalar:\n"
            return response
    
    # MENU 4: Save report
    if len(parts) == 3:
        lang = "English" if parts[0] == "1" else "Hausa"
        issue_type = parts[1]
        description = parts[2]
        
        full_report = f"Type:{issue_type} - {description}"
        save_report(phone, full_report, lang)
        
        if parts[0] == "1":
            return "END Thank you! We received your report. We will act on it."
        else:
            return "END Nagode! Mun karbi sako."

@app.route('/reports', methods=['GET'])
def view_reports():
    try:
        with open(REPORTS_FILE, 'r') as f:
            data = json.load(f)
        return {"reports": data, "count": len(data)}
    except:
        return {"reports": [], "count": 0}

@app.route('/murya', methods=['GET'])
def home():
    return "MURYA USSD is live! Use POST only."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)