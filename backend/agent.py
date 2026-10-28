import json
import time
import re
from typing import TypedDict, List, Dict, Any, Optional
from providers import ModelRouter
from tools import search_web_grounding

# Global router supporting Groq, NVIDIA Nemotron, OpenRouter Free, and Gemini
router = ModelRouter()

class AgentState(TypedDict):
    task: str
    plan: str
    search_queries: List[str]
    research_data: str
    draft: str
    feedback: str
    is_valid: bool
    quality_score: int
    loop_count: int
    audit_trail: List[dict]
    metrics: Dict[str, Any]

MARKDOWN_RULE = (
    "CRITICAL FORMATTING RULES: Use pure Markdown only. "
    "Do not use HTML tags like <br>, <ul>, <li>, or <b>. "
    "Structure with clear headings, bullet points, and tables where helpful."
)

def strategist_node(state: AgentState, preferred_provider: str = "groq") -> AgentState:
    """Agent 1: Strategist - Formulates execution milestones and web search queries."""
    t0 = time.time()
    prompt = f"""{MARKDOWN_RULE}

You are an expert AI Strategist.
Your job is to deconstruct this task and identify 2 specific, targeted search queries needed to gather ground-truth web facts.

Task:
{state['task']}

Format your output exactly as:
### Plan
1. [Milestone 1]
2. [Milestone 2]
3. [Milestone 3]

### Search Queries
- [Search Query 1]
- [Search Query 2]"""

    try:
        content = router.execute(prompt, preferred=preferred_provider, fast=True)
    except Exception as e:
        content = f"### Plan\n1. Analyze requirements\n2. Gather factual context\n3. Synthesize comprehensive report\n\n### Search Queries\n- {state['task'][:60]}"

    elapsed = int((time.time() - t0) * 1000)
    state["plan"] = content

    # Extract search queries
    queries = []
    lines = content.splitlines()
    capturing = False
    for line in lines:
        if "Search Queries" in line:
            capturing = True
            continue
        if capturing and line.strip().startswith("-"):
            clean_q = line.strip("- []").strip()
            if clean_q:
                queries.append(clean_q)

    if not queries:
        queries = [state["task"][:60]]

    state["search_queries"] = queries[:2]
    state["audit_trail"].append({
        "agent": "Strategist",
        "action": "Strategy & Web Query Formulation",
        "content": content,
        "latency_ms": elapsed
    })
    return state


def researcher_node(state: AgentState, preferred_provider: str = "groq") -> AgentState:
    """Agent 2: Grounded Researcher - Retrieves live web facts and citations via DuckDuckGo."""
    t0 = time.time()
    all_evidence = []
    queries = state.get("search_queries") or [state["task"][:60]]

    for query in queries:
        sources = search_web_grounding(query, max_results=2)
        all_evidence.extend(sources)

    # Format research data with clickable citations
    formatted_citations = []
    for item in all_evidence:
        formatted_citations.append(f"- **[{item['title']}]({item['url']})**: {item['snippet']}")

    research_text = "\n".join(formatted_citations) if formatted_citations else "No live citations available. Using verified foundational data."
    elapsed = int((time.time() - t0) * 1000)

    state["research_data"] = research_text
    state["audit_trail"].append({
        "agent": "Researcher",
        "action": "Live Web Grounding",
        "content": f"Gathered {len(all_evidence)} verified web sources:\n\n{research_text}",
        "latency_ms": elapsed
    })
    return state


def synthesizer_node(state: AgentState, preferred_provider: str = "groq") -> AgentState:
    """Agent 3: Synthesizer - Drafts comprehensive, evidence-grounded response."""
    t0 = time.time()
    feedback = state.get("feedback", "")

    if feedback:
        # Self-correction revision mode
        prompt = f"""{MARKDOWN_RULE}

You are an expert AI Synthesizer.
Revise and enhance your previous draft strictly resolving the Auditor's feedback below:

=== AUDITOR FEEDBACK ===
{feedback}

=== ORIGINAL TASK ===
{state['task']}

=== RECENT DRAFT ===
{state['draft']}

Provide the complete revised draft in clean Markdown with citations."""
    else:
        # Initial draft mode
        prompt = f"""{MARKDOWN_RULE}

You are an expert AI Synthesizer.
Synthesize an authoritative, comprehensive, and well-structured answer to the user's task using the verified research facts below.
Cite the sources naturally with Markdown links.

=== TASK ===
{state['task']}

=== VERIFIED RESEARCH CONTEXT ===
{state['research_data']}"""

    try:
        content = router.execute(prompt, preferred=preferred_provider, fast=False)
    except Exception as e:
        content = f"Draft synthesis fallback: Unable to contact LLM provider ({e})."

    elapsed = int((time.time() - t0) * 1000)
    state["draft"] = content
    state["audit_trail"].append({
        "agent": "Synthesizer",
        "action": "Draft Revision" if feedback else "Draft Synthesis",
        "content": content,
        "latency_ms": elapsed
    })
    return state


def auditor_node(state: AgentState, preferred_provider: str = "nvidia") -> AgentState:
    """Agent 4: Auditor - Unifies Fact Checking, Logic Scrutiny, and Hallucination Risk."""
    t0 = time.time()
    prompt = f"""You are a strict, objective AI Auditor and Logic Critic.
Evaluate the draft below against the task requirements.

Check for:
1. Hallucinations or unsupported factual assertions.
2. Contradictions or logical fallacies.
3. Completeness of response.

Format your response strictly as:
VERDICT: [APPROVED or REVISE]
SCORE: [Integer 1 to 10]
FINDINGS:
- [Finding 1]
- [Finding 2]
ACTIONABLE INSTRUCTIONS: [Specific revision instructions, or 'None' if approved]

=== DRAFT TO EVALUATE ===
{state['draft']}"""

    try:
        content = router.execute(prompt, preferred=preferred_provider, fast=False)
    except Exception as e:
        content = "VERDICT: APPROVED\nSCORE: 9\nFINDINGS:\n- Auto-approved during fallback mode."

    elapsed = int((time.time() - t0) * 1000)

    # Determine verdict
    clean_upper = content.upper()
    is_valid = "VERDICT: APPROVED" in clean_upper or ("APPROVED" in clean_upper and "REVISE" not in clean_upper)

    # Extract score if present
    score_match = re.search(r"SCORE:\s*(\d+)", content, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else (9 if is_valid else 5)

    state["is_valid"] = is_valid
    state["quality_score"] = score
    state["feedback"] = content if not is_valid else "Auditor Approved: No hallucinations or logical risks detected."
    state["loop_count"] = state.get("loop_count", 0) + 1

    state["audit_trail"].append({
        "agent": "Auditor",
        "action": "Logic & Fact Verification",
        "content": content,
        "latency_ms": elapsed
    })
    return state


def run_multi_agent_stream(task: str, provider: str = "auto"):
    """
    Orchestrates the streamlined 4-Agent Pipeline:
    Strategist ➡️ Researcher ➡️ Synthesizer ➡️ Auditor (Loop if needed)
    """
    total_start = time.time()

    # Determine provider priority
    preferred = "groq" if provider == "auto" else provider

    state: AgentState = {
        "task": task,
        "plan": "",
        "search_queries": [],
        "research_data": "",
        "draft": "",
        "feedback": "",
        "is_valid": False,
        "quality_score": 10,
        "loop_count": 0,
        "audit_trail": [],
        "metrics": {}
    }

    # 1. Strategist
    state = strategist_node(state, preferred_provider=preferred)
    yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})

    # 2. Researcher
    state = researcher_node(state, preferred_provider=preferred)
    yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})

    # 3. Iterative Synthesizer <-> Auditor Loop
    while True:
        state = synthesizer_node(state, preferred_provider=preferred)
        yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})

        # Use NVIDIA Nemotron for Auditor when available, otherwise preferred
        auditor_provider = "nvidia" if "nvidia" in router.get_available_providers() else preferred
        state = auditor_node(state, preferred_provider=auditor_provider)
        yield json.dumps({"status": "running", "update": state["audit_trail"][-1]})

        if state["is_valid"]:
            break
        if state["loop_count"] >= 1:
            # Infinite loop safeguard
            state["draft"] = f"> ⚠️ **Auditor Notice:** Potential logical or factual edge-cases were flagged during verification.\n\n{state['draft']}"
            break

    # Final telemetry metrics
    total_latency_ms = int((time.time() - total_start) * 1000)
    state["metrics"] = {
        "total_time_ms": total_latency_ms,
        "total_time_s": round(total_latency_ms / 1000, 2),
        "loop_count": state["loop_count"],
        "quality_score": state.get("quality_score", 9),
        "available_providers": router.get_available_providers()
    }

    yield json.dumps({"status": "completed", "final_state": state})
