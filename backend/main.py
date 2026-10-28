from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from agent import run_multi_agent_stream, router

app = Flask(__name__)
CORS(app)  # Allow Next.js frontend to communicate with Flask

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({
        "message": "VersatileAI Multi-Agent Verification Backend is running!",
        "available_providers": router.get_available_providers()
    })

@app.route("/api/providers", methods=["GET"])
def get_providers():
    return jsonify({
        "providers": router.get_available_providers(),
        "free_tier_guaranteed": True
    })

@app.route("/api/run-task", methods=["POST"])
def run_task():
    data = request.json or {}
    prompt = data.get("prompt", "")
    provider = data.get("provider", "auto")
    
    def generate():
        for chunk in run_multi_agent_stream(prompt, provider=provider):
            yield f"data: {chunk}\n\n"
            
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(port=8000, debug=True)
