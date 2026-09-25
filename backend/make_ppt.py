from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Create presentation
prs = Presentation()

# Slide 1: Title Slide
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "Antigravity Orchestrator"
subtitle.text = "A Multi-Agent AI System Designed to Eliminate Hallucinations\nBuilt for Speed, Reliability, and Scale"

# Slide 2: The Problem & Vision
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
title.text = "The Problem & Our Vision"
content = slide.placeholders[1].text_frame
content.text = "The Hallucination Problem in AI:"
p = content.add_paragraph()
p.text = "Single-agent LLMs (like standard ChatGPT) hallucinate, fail at complex multi-step reasoning, and lack self-correction."
p.level = 1
p = content.add_paragraph()
p.text = "Our Vision:"
p = content.add_paragraph()
p.text = "A self-correcting, highly reliable Multi-Agent Swarm that plans, researches, writes, verifies, and critiques its own work."
p.level = 1
p = content.add_paragraph()
p.text = "Result: 100% verified output that users can actually trust."

# Slide 3: The Architecture
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "The Multi-Agent Pipeline"
content = slide.placeholders[1].text_frame
content.text = "A 5-Stage Orchestration Pipeline:"
p = content.add_paragraph()
p.text = "1. Planner: Breaks the task into logical steps."
p.level = 1
p = content.add_paragraph()
p.text = "2. Researcher: Gathers factual data based on the plan."
p.level = 1
p = content.add_paragraph()
p.text = "3. Coder/Writer: Drafts the response using pure Markdown."
p.level = 1
p = content.add_paragraph()
p.text = "4. Verifier: Fact-checks the draft against the research."
p.level = 1
p = content.add_paragraph()
p.text = "5. Critic: Analyzes logic and flags risks."
p.level = 1
p = content.add_paragraph()
p.text = "Auto-Refinement: The system loops back and rewrites automatically if the Critic flags an issue."

# Slide 4: Optimization & Execution
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Engineered for Speed and Scale"
content = slide.placeholders[1].text_frame
content.text = "Dual-Model Smart Routing:"
p = content.add_paragraph()
p.text = "Lightweight tasks (Planning, Verifying) use an ultra-fast, cheap model (gpt-oss-20b)."
p.level = 1
p = content.add_paragraph()
p.text = "Complex drafting uses a heavy, powerful model (gpt-oss-120b)."
p.level = 1
p = content.add_paragraph()
p.text = "Context Optimization:"
p = content.add_paragraph()
p.text = "Agents are strictly bounded by CONCISENESS RULES (max 150 words) to prevent token bloat."
p.level = 1
p = content.add_paragraph()
p.text = "Fault Tolerance: Built-in automatic API retries and rate-limit handling."

# Slide 5: Innovation & UI
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "User Experience & Innovation"
content = slide.placeholders[1].text_frame
content.text = "Premium, Transparent Interface:"
p = content.add_paragraph()
p.text = "Real-time Streaming: Users see exactly what the Swarm is thinking via a Server-Sent Events (SSE) audit trail."
p.level = 1
p = content.add_paragraph()
p.text = "Beautiful Render: Outputs are rendered in strict, sanitized Markdown."
p.level = 1
p = content.add_paragraph()
p.text = "Beyond Chatbots: This is an Autonomous Worker, not just a conversational bot."
p = content.add_paragraph()
p.text = "Perfect for legal drafting, medical research, and coding where hallucinations cause critical failures."
p.level = 1

# Slide 6: Future Roadmap
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Future Roadmap & Conclusion"
content = slide.placeholders[1].text_frame
content.text = "What's Next?"
p = content.add_paragraph()
p.text = "Web Browsing Agent: Scrape live data directly from the web."
p.level = 1
p = content.add_paragraph()
p.text = "Code Execution: Allow the Coder agent to run Python code in a secure sandbox."
p.level = 1
p = content.add_paragraph()
p.text = "Conclusion:"
p = content.add_paragraph()
p.text = "\"The future of AI isn't one giant model; it's a swarm of specialized agents working together.\""
p.level = 1

prs.save(r"c:\Users\nerli\Desktop\MBU hackathon\Antigravity_Pitch_Deck.pptx")
print("Saved PPTX successfully!")
