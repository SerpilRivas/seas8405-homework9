from flask import Flask, request, jsonify
import os
import re
import ast
from ping3 import ping

app = Flask(__name__)
print("🔥 Flask app loaded with updated code!")

# Load password securely from environment
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

# AST-secure /calculate route
@app.route('/calculate')
def calculate():
    expression = request.args.get('expr', '').strip()

    # Only allow safe math characters
    if not re.match(r'^[\d\+\-\*/\(\)\.\s]+$', expression):
        return "Invalid expression format", 400

    # Remove whitespace
    expression = re.sub(r'\s+', '', expression)

    try:
        # Parse and check allowed AST nodes
        node = ast.parse(expression, mode='eval')
        for subnode in ast.walk(node):
            if not isinstance(subnode, (
                ast.Expression, ast.BinOp, ast.UnaryOp,
                ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div,
                ast.Pow, ast.USub, ast.UAdd, ast.Load, ast.Constant
            )):
                return "Invalid or unsafe expression", 400

        result = eval(compile(node, "<string>", mode="eval"))
        return jsonify({'result': result})

    except Exception:
        return "Invalid or unsafe expression", 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
