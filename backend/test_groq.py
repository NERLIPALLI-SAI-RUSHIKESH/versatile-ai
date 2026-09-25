import os
key = os.environ.get("GROQ_API_KEY", "your_key_here")
headers = {"Authorization": f"Bearer {key}"}
res = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
print([m["id"] for m in res.json().get("data", [])])
