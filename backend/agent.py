import os
from openai import OpenAI
from typing import TypedDict, List
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key or api_key == "your_key_here":
    print("WARNING: OPENROUTER_API_KEY is not set in .env!")

import requests

groq_api_key = os.environ.get("GROQ_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

if groq_api_key:
    BASE_URL = "https://api.groq.com/openai/v1"
    API_KEY = groq_api_key
    MODEL_NAME = "openai/gpt-oss-120b"
    FAST_MODEL = "openai/gpt-oss-20b"
    FALLBACK_MODEL = "openai/gpt-oss-20b"
else:
    BASE_URL = "https://openrouter.ai/api/v1"
    API_KEY = openrouter_api_key
    MODEL_NAME = "google/gemma-4-31b-it:free"
    FAST_MODEL = "nvidia/nemotron-3.5-lightning:free"
    FALLBACK_MODEL = "nvidia/nemotron-3.5-lightning:free"

class AgentState(TypedDict):
    task: str
    plan: str
    research_data: str
    draft: str
    feedback: str
    is_valid: bool
    loop_count: int
    audit_trail: List[dict]

import time

def _post_request(model_name: str, prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity" # Bypass buggy decompression
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # Auto-retry logic for 429 Too Many Requests
    for attempt in range(5):
        response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
        if response.status_code == 429:
            print(f"Groq speed limit hit. Pausing for 5 seconds... (Attempt {attempt+1}/5)")
            time.sleep(5)
            continue
            
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
        
    raise Exception("API ERROR: Rate limit exceeded after 5 retries.")

def call_llm(prompt: str, model_override: str = None) -> str:
    target_model = model_override or MODEL_NAME
    try:
        return _post_request(target_model, prompt)
    except Exception as e:
        print(f"Primary model failed. Falling back... ({e})")
        try:
            return _post_request(FALLBACK_MODEL, prompt)
        except Exception as e2:
            print(f"Both models failed... ({e2})")
            return "ERROR: We have completely exhausted the daily API rate limit (429 Too Many Requests). Please try again tomorrow or use a different API key."

CONCISE_RULE = "CONCISENESS RULE: Be extremely concise. Output no more than 150 words."
MARKDOWN_RULE = "CRITICAL FORMATTING RULES: Use ONLY pure Markdown. Never use any HTML tags like <br>, <ul>, <li>, <b>, or any other HTML. For lists inside tables, use a new line with a dash (-) outside the table instead. Output must render cleanly in a Markdown renderer."

def planner_node(state: AgentState):
    prompt = f"{CONCISE_RULE}\n{MARKDOWN_RULE}\n\nYou are an expert AI Planner. Break this task into 3 clear, concise steps using Markdown headings and bullet points:\n\n=== TASK ===\n{state['task']}"
    content = call_llm(prompt, model_override=FAST_MODEL)
    state["plan"] = content
    state["audit_trail"].append({"agent": "Planner", "action": "Created Plan", "content": content})
    return state

def researcher_node(state: AgentState):
    prompt = f"{CONCISE_RULE}\n{MARKDOWN_RULE}\n\nYou are an AI Researcher. Provide your findings as a bulleted summary of EXACTLY 5 POINTS MAXIMUM needed to execute this plan:\n\n=== PLAN ===\n{state['plan']}"
    content = call_llm(prompt, model_override=FAST_MODEL)
    state["research_data"] = content
    state["audit_trail"].append({"agent": "Researcher", "action": "Gathered Data", "content": content})
    return state

def coder_node(state: AgentState):
    feedback = state.get("feedback", "")
    if feedback:
        prompt = f"{MARKDOWN_RULE}\n\nYou are an expert AI Writer.\nFix your previous draft based on this feedback. Output in clean Markdown only.\n\n=== FEEDBACK ===\n{feedback}\n\n=== ORIGINAL TASK ===\n{state['task']}"
    else:
        prompt = f"{MARKDOWN_RULE}\n\nYou are an expert AI Writer.\nWrite a clear, well-structured response using Markdown headings, bullet points, and tables (no HTML at all).\n\n=== TASK ===\n{state['task']}\n\n=== RESEARCH CONTEXT ===\n{state['research_data']}"
        
    content = call_llm(prompt)
    state["draft"] = content
    state["audit_trail"].append({"agent": "Coder", "action": "Wrote Draft", "content": content})
    return state

def verifier_node(state: AgentState):
    prompt = f"You are a strict Fact Checker. Verify the facts in the draft below.\nOutput ONLY 'VERIFIED' or 'ERRORS FOUND' followed by the details.\n\n=== DRAFT ===\n{state['draft']}"
    content = call_llm(prompt, model_override=FAST_MODEL)
    state["audit_trail"].append({"agent": "Verifier", "action": "Fact Check", "content": content})
    return state

def critic_node(state: AgentState):
    draft = state.get("draft", "")
    prompt = f"You are a strict Logic and Risk Critic.\nIf the draft below answers the task perfectly without hallucinations, output the word VALID.\nIf there are logic flaws, output the word REJECTED followed by what needs to be fixed.\n\n=== DRAFT TO EVALUATE ===\n{draft}"
    
    content = call_llm(prompt, model_override=FAST_MODEL)
    content_clean = content.strip().upper().replace("*", "").replace("`", "")
    
    # Check if the word VALID is present and REJECTED is not.
    if "VALID" in content_clean and "REJECTED" not in content_clean:
        is_valid = True
        feedback = "Critic approved: No risks or hallucinations detected."
    else:
        is_valid = False
        feedback = content
        
    state["is_valid"] = is_valid
    state["feedback"] = feedback
    state["loop_count"] = state.get("loop_count", 0) + 1
    state["audit_trail"].append({"agent": "Critic", "action": "Risk Assessment", "content": feedback})
    return state

def finalizer_node(state: AgentState):
    if not state.get("is_valid"):
        final_output = f"> **Critic Warning:** The Critic agent flagged potential issues with this draft, but the maximum refinement loop was reached.\n\n{state['draft']}"
    else:
        final_output = f"{state['draft']}"
        
    state["draft"] = final_output
    state["audit_trail"].append({"agent": "Finalizer", "action": "Formatted Output", "content": "Processed final output."})
    return state

import json

def run_multi_agent_stream(task: str):
    state: AgentState = {
        "task": task,
        "plan": "",
        "research_data": "",
        "draft": "",
        "feedback": "",
        "is_valid": False,
        "loop_count": 0,
        "audit_trail": []
    }
    
    state = planner_node(state)
    yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
    
    state = researcher_node(state)
    yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
    
    while True:
        state = coder_node(state)
        yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
        
        state = verifier_node(state)
        yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
        
        state = critic_node(state)
        yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
        
        if state["is_valid"]:
            break 
        if state["loop_count"] >= 1:
            break 
            
    state = finalizer_node(state)
    yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})
    yield json.dumps({"status": "completed", "final_state": state})
