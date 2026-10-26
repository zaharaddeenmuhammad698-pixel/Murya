from flask import Flask, request
app = Flask(__name__)

@app.route('/murya', methods=['POST'])
def murya():
    text = request.values.get("text","")
    phone = request.values.get("phoneNumber")
    if text == "":
        return "CON Welcome to MURYA - Murya Jama'a\n1. English\n2. Hausa"
    elif text == "1":
        return "CON MURYA - Bauchi\n1. Report Issue\n2. Find Polling Unit\n3. Election Info"
    elif text == "1*1":
        return "CON Report:\n1. No ballot\n2. Violence\n3. BVAS not working"
    elif text.startswith("1*1*"):
        return f"END Thank you! Report from {phone} received. Ref saved."
    elif text == "1*2":
        return "CON Enter Ward/LGA:"
    elif text.startswith("1*2*"):
        return "END PU: Bauchi Central Primary School. Check SMS."
    elif text == "2":
        return "CON MURYA - Taimako\n1. Kai Korafi\n2. Nemo Wurin Zabe\n3. Bayanin Zabe"
    elif text.startswith("2*1*") or text.startswith("1*3") or text.startswith("2*3"):
        return "END Nagode! Mun karbi sako."
    else:
        return "END Invalid. Dial *384*13833# again."

@app.route('/')
def home():
    return "MURYA USSD Live"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)