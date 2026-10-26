from flask import Flask, request
import os, requests

app = Flask(__name__)

BAUCHI_LGAS = {
 "bauchi": "Bauchi LGA INEC Office, Yakubun Bauchi Road, Bauchi",
 "toro": "Toro LGA INEC Office, Magama Gumau, Toro",
 "alkaleri": "Alkaleri LGA INEC Office, Alkaleri",
 "misau": "Misau LGA INEC Office, Misau",
 "katagum": "Katagum LGA INEC Office, Azare",
}

def kb_match(text):
    t = text.lower()
    for lga, addr in BAUCHI_LGAS.items():
        if lga in t:
            return f"Ofishin INEC na {lga.title()}: {addr}. Tabbatar: inec.gov.ng", 1.0
    if "pvc" in t:
        return "Duba PVC: voters.inecnigeria.org - Independent civic-tech, not official INEC", 0.9
    return "Tambayarka an karba. Ziyarci inec.gov.ng - Independent project, not INEC", 0.0

@app.route("/")
def home():
    return "MURYA WhatsApp Bot V4-B Live"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == os.getenv("VERIFY_TOKEN", "murya_bauchi_2027"):
            return request.args.get("hub.challenge")
        return "Wrong token", 403
    data = request.json
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        text = msg['text']['body']
        from_num = msg['from']
        ans, _ = kb_match(text)
        # Here you would send back via WhatsApp API - we do next bit
        print(f"Reply to {from_num}: {ans}")
    except: pass
    return "OK", 200