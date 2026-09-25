from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from agent import run_multi_agent_stream

app = Flask(__name__)
CORS(app) # Allow Next.js to communicate with Flask

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Verification Engine Backend is running!"})

@app.route("/api/run-task", methods=["POST"])
def run_task():
    data = request.json
    prompt = data.get("prompt", "")
    
    def generate():
        for chunk in run_multi_agent_stream(prompt):
            yield f"data: {chunk}\n\n"
            
    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(port=8000, debug=True)
