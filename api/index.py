from flask import Flask, request, Response, jsonify
import requests
import os
import json

app = Flask(__name__)

# Configuration (These will come from Vercel Environment Variables)
OCI_VM_URL = os.environ.get("OCI_VM_URL", "http://141.148.202.95")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "platform": "vercel"})

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chat_proxy():
    if request.method == 'OPTIONS':
        return Response(status=204)
        
    data = request.json
    model = data.get("model", "")
    
    # Priority Routing Logic
    # 1. Groq models
    if any(m in model for m in ["llama-3.1", "llama-3.3", "mixtral", "gemma-2-9b"]):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        resp = requests.post(url, json=data, headers=headers, stream=True)
        return Response(resp.iter_content(chunk_size=1024), content_type=resp.headers['Content-Type'])

    # 2. Local OCI models
    else:
        url = f"{OCI_VM_URL}/v1/chat/completions"
        resp = requests.post(url, json=data, stream=True)
        return Response(resp.iter_content(chunk_size=1024), content_type=resp.headers['Content-Type'])

# Add other routes as needed (models, history, etc)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"error": "Not Found", "path": path}), 404

if __name__ == '__main__':
    app.run()
