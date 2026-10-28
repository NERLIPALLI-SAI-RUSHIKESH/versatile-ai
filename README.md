<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&pause=1000&color=6366F1&center=true&vCenter=true&width=700&lines=VersatileAI+%F0%9F%A4%96;4-Agent+Multi-Model+AI+Platform;Plan+%E2%86%92+Research+%E2%86%92+Synthesize+%E2%86%92+Verify" alt="Typing SVG" />

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://versatile-ai-delta.vercel.app/)
[![Backend](https://img.shields.io/badge/⚡_Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://versatile-ai.onrender.com)
[![GitHub Stars](https://img.shields.io/github/stars/NERLIPALLI-SAI-RUSHIKESH/versatile-ai?style=for-the-badge&color=FFD700&logo=github)](https://github.com/NERLIPALLI-SAI-RUSHIKESH/versatile-ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-6366F1?style=for-the-badge)](LICENSE)

<br/>

[![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Next.js](https://img.shields.io/badge/Next.js_15-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/Groq_LPU-F05A28?style=flat-square)](https://groq.com/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA_Nemotron-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://build.nvidia.com/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-6366F1?style=flat-square)](https://openrouter.ai/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com/)

<br/>

> **Single LLMs hallucinate. VersatileAI doesn't.**
> 
> Four specialized AI agents — each with a distinct role — collaborate in a pipeline to plan, research live web data, synthesize, and fact-check every response before you see it.

</div>

---

## 🎯 The Problem We Solve

| ❌ Normal AI Chatbot | ✅ VersatileAI |
|---|---|
| One model does everything | 4 specialized agents, each expert at one job |
| Hallucinations with no check | Auditor agent scores & flags every response |
| No sources, no citations | Live DuckDuckGo web search with source URLs |
| You trust blindly | You see the full reasoning chain + latency |
| Black box | Fully transparent agent-by-agent pipeline |

---

## 🧠 4-Agent Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER PROMPT                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  1. 🗺️  STRATEGIST      │  ← Groq gpt-oss-20b (fast)
        │  Decomposes query into  │
        │  milestones + search    │
        │  queries                │
        └────────────┬────────────┘
                     │  search queries
                     ▼
        ┌─────────────────────────┐
        │  2. 🔬  RESEARCHER      │  ← DuckDuckGo Live Search
        │  Fetches real-time web  │
        │  citations & snippets   │
        └────────────┬────────────┘
                     │  grounded facts + URLs
                     ▼
        ┌─────────────────────────┐
        │  3. ✍️  SYNTHESIZER     │  ← Groq gpt-oss-120b (heavy)
        │  Writes structured      │
        │  markdown report with   │
        │  inline citations       │
        └────────────┬────────────┘
                     │  draft report
                     ▼
        ┌─────────────────────────┐
        │  4. ⚖️  AUDITOR         │  ← OpenRouter Nemotron (free)
        │  Fact-checks, scores    │
        │  quality 0-10, flags    │
        │  hallucinations         │
        └────────────┬────────────┘
                     │  APPROVED ✅ / REVISE ↩️
                     ▼
        ┌─────────────────────────┐
        │   FINAL VERIFIED        │
        │   RESPONSE + TELEMETRY  │
        │   (score, latency, src) │
        └─────────────────────────┘
```

---

## ⚡ Free Multi-Model Gateway

Built with a **Universal Model Router** that auto-cascades across 100% free providers with failover:

| # | Provider | Model | Speed | Strengths |
|---|---|---|---|---|
| 1 | **Groq Cloud** | `gpt-oss-20b` + `gpt-oss-120b` | ⚡ Sub-second LPU | Planning + heavy synthesis |
| 2 | **OpenRouter** | `nvidia/nemotron-3.5-lightning:free` | 🚀 Fast | Fact auditing, zero cost |
| 3 | **NVIDIA NIM** | `llama-3.1-nemotron-70b` | 🔥 Powerful | Backup heavy reasoning |
| 4 | **Google Gemini** | `gemini-2.0-flash` | ⚡ Fast | If valid key provided |

> **Zero paid API calls. Ever.** Every model is on a free tier. The `:free` tag is enforced in code as a hard guardrail.

---

## 🖥️ Screenshots

<div align="center">

| 4-Agent Pipeline Live View | Dark Glassmorphism UI |
|---|---|
| Agents light up in real-time with latency badges | Full dark mode with ambient gradients |

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+  
- Node.js 18+

### 1. Clone the repo
```bash
git clone https://github.com/NERLIPALLI-SAI-RUSHIKESH/versatile-ai.git
cd versatile-ai
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:
```env
GROQ_API_KEY=gsk_your_groq_key_here
OPENROUTER_API_KEY=sk-or-v1_your_openrouter_key_here
NVIDIA_API_KEY=nvapi_your_nvidia_key_here
PORT=8000
```

**Get free API keys:**
- 🟠 Groq → https://console.groq.com (free, no credit card)
- 🟣 OpenRouter → https://openrouter.ai (free tier, no credit card)
- 🟢 NVIDIA → https://build.nvidia.com (1000 free credits)

Start the server:
```bash
python main.py
```
Backend running at `http://localhost:8000` ✅

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` ✅

### 4. Docker (Full Stack)
```bash
docker compose up --build
```

---

## 🧪 Testing

Run the full backend test suite (8 tests):
```bash
cd backend
python -m unittest test_agent.py -v
```

Expected output:
```
test_agent_pipeline_structure ... ok
test_auditor_node ... ok
test_groq_client_init ... ok
test_infinite_loop_safeguard ... ok
test_model_router_fallback ... ok
test_openrouter_client_init ... ok
test_researcher_node ... ok
test_strategist_node ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.XXXs
OK
```

---

## 📡 API Reference

### `POST /api/run-task`
Streams multi-agent reasoning via **Server-Sent Events (SSE)**.

```bash
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Latest AI breakthroughs 2024", "provider": "auto"}'
```

**Request body:**
```json
{
  "prompt": "Your question here",
  "provider": "auto"
}
```
`provider` options: `auto` | `groq` | `openrouter` | `nvidia`

**Response stream (`text/event-stream`):**
```json
{"status": "running", "agent": "strategist", "output": "...", "latency_ms": 412}
{"status": "running", "agent": "researcher", "output": "...", "latency_ms": 850}
{"status": "running", "agent": "synthesizer", "output": "...", "latency_ms": 2100}
{"status": "completed", "agent": "auditor", "score": 9, "verdict": "APPROVED", "latency_ms": 1800}
```

### `GET /api/providers`
Returns active model providers.

```json
{
  "providers": ["groq", "openrouter"],
  "count": 2
}
```

---

## 🗂️ Project Structure

```
versatile-ai/
├── backend/
│   ├── main.py           # Flask server + SSE endpoints
│   ├── agent.py          # 4-agent LangGraph pipeline
│   ├── providers.py      # Universal multi-model gateway
│   ├── tools.py          # DuckDuckGo live search tool
│   ├── test_agent.py     # 8 unit tests (all passing ✅)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/
│   │   └── page.tsx      # Main UI — dark glassmorphism
│   ├── package.json
│   └── Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml        # GitHub Actions CI pipeline
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS |
| **Backend** | Python 3.11, Flask, LangGraph |
| **AI Orchestration** | LangGraph state machine (4-node pipeline) |
| **LLM Providers** | Groq Cloud, OpenRouter, NVIDIA NIM |
| **Web Grounding** | DuckDuckGo Search API (real-time citations) |
| **Streaming** | Server-Sent Events (SSE) |
| **Deployment** | Vercel (frontend) + Render (backend) |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker + Docker Compose |

---

## 🌐 Deployment

| Service | Platform | URL |
|---|---|---|
| Frontend | Vercel | https://versatile-ai-delta.vercel.app/ |
| Backend | Render | https://versatile-ai.onrender.com |

### Environment Variables

**Render (Backend):**
```
GROQ_API_KEY=...
OPENROUTER_API_KEY=...
NVIDIA_API_KEY=...
PORT=8000
```

**Vercel (Frontend):**
```
NEXT_PUBLIC_API_URL=https://your-render-url.onrender.com
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m "feat: add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">

**Built for MBU Hackathon 2024 — by Nerlipalli Sai Rushikesh**

⭐ Star this repo if you found it useful!

[![GitHub](https://img.shields.io/badge/GitHub-NERLIPALLI--SAI--RUSHIKESH-181717?style=for-the-badge&logo=github)](https://github.com/NERLIPALLI-SAI-RUSHIKESH)

</div>
