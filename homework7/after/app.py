from flask import Flask, request, jsonify
import os
import re
import sympy
from ping3 import ping

app = Flask(__name__)
print("🔥 Flask app loaded with updated code!")

# Hard-coded password
PASSWORD = os.getenv("APP_PASSWORD", "changeme")

@app.route('/')
def hello():
    name = request.args.get('name', 'World')
    if not name.isalnum():
        return jsonify({"error": "Invalid name"}), 400
    return f"Hello, {name}! (Secure Version)"

# Secure ping route using ping3
@app.route('/ping')
def do_ping():
    ip = request.args.get('ip', '').strip()
    print(f"Received IP: {ip}")

    # Reject dangerous characters
    if any(c in ip for c in [';', '&', '|', ' ', '`']):
        print(f"Invalid IP: contains dangerous characters: {ip}")
        return "Invalid IP address", 400

    # Validate IPv4 format
    if not re.match(r'^\d{1,3}(\.\d{1,3}){3}$', ip):
        print(f"Invalid IP: doesn't match IPv4 pattern: {ip}")
        return "Invalid IP address", 400

    try:
        response = ping(ip, timeout=2)
        if response is None:
            return "Ping failed", 500
        return jsonify({'latency': response})
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/calculate')
def calculate():
    expression = request.args.get('expr', '').strip()

    # Reject empty or invalid characters
    if not re.match(r'^[\d\+\-\*/\(\)\.\s]+$', expression):
        return "Invalid expression format", 400

    # Remove extra spaces
    expression = re.sub(r'\s+', '', expression)

    try:
        result = sympy.sympify(expression, evaluate=True)

        # Check for undefined/infinite values
        if result.is_infinite or result.has(sympy.zoo):
            return "Division by zero is not allowed", 400

        return jsonify({'result': float(result)})
    except (sympy.SympifyError, ZeroDivisionError):
        return "Invalid expression", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) # nosec B104


