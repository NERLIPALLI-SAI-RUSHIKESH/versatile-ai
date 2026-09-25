import traceback
from agent import client, MODEL_NAME
try:
    client.chat.completions.create(model=MODEL_NAME, messages=[{"role": "user", "content": "hi"}])
except Exception as e:
    traceback.print_exc()
