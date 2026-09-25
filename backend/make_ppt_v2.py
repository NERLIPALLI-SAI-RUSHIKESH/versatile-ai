from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import pptx.oxml.ns as nsmap
from lxml import etree

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# ── COLOUR PALETTE ──────────────────────────────────────────
DARK_BG   = RGBColor(0x0D, 0x1B, 0x2A)   # deep navy
ACCENT    = RGBColor(0x00, 0xB4, 0xD8)   # electric cyan
GOLD      = RGBColor(0xFF, 0xC3, 0x00)   # amber/gold
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG  = RGBColor(0x12, 0x28, 0x3E)   # slightly lighter navy
CARD_BG   = RGBColor(0x1A, 0x35, 0x52)   # card surface
MID_GRAY  = RGBColor(0xB0, 0xC4, 0xDE)   # light-steel-blue for body text
GREEN     = RGBColor(0x2E, 0xCC, 0x71)
RED       = RGBColor(0xE7, 0x4C, 0x3C)
PURPLE    = RGBColor(0x95, 0x63, 0xF8)

# ── HELPERS ─────────────────────────────────────────────────
def blank_slide():
    layout = prs.slide_layouts[6]   # completely blank
    return prs.slides.add_slide(layout)

def solid_bg(slide, colour):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = colour

def add_rect(slide, left, top, width, height, fill_colour, alpha=None):
    shape = slide.shapes.add_shape(1, Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_colour
    shape.line.fill.background()   # no border
    return shape

def add_text(slide, text, left, top, width, height,
             size=18, bold=False, colour=WHITE, align=PP_ALIGN.LEFT,
             italic=False, wrap=True):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top),
                                     Inches(width), Inches(height))
    txBox.word_wrap = wrap
    tf = txBox.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = colour
    return txBox

def add_bullet_box(slide, items, left, top, width, height,
                   title=None, title_colour=ACCENT, body_colour=MID_GRAY,
                   bg_colour=CARD_BG, body_size=13, title_size=15):
    add_rect(slide, left, top, width, height, bg_colour)
    y = top + 0.18
    if title:
        add_text(slide, title, left+0.18, y, width-0.36, 0.38,
                 size=title_size, bold=True, colour=title_colour)
        y += 0.42
    for item in items:
        add_text(slide, f"▸  {item}", left+0.18, y, width-0.36, 0.35,
                 size=body_size, colour=body_colour)
        y += 0.38

def header_bar(slide, title, subtitle=None):
    # dark top bar
    add_rect(slide, 0, 0, 13.33, 1.35, DARK_BG)
    # cyan accent stripe
    add_rect(slide, 0, 1.35, 13.33, 0.07, ACCENT)
    add_text(slide, title, 0.5, 0.12, 12, 0.6,
             size=30, bold=True, colour=WHITE)
    if subtitle:
        add_text(slide, subtitle, 0.5, 0.72, 12, 0.5,
                 size=14, colour=ACCENT)

# ══════════════════════════════════════════════════════════════
#  SLIDE 1 — TITLE
# ══════════════════════════════════════════════════════════════
s1 = blank_slide()
solid_bg(s1, DARK_BG)
# large gradient-like left block
add_rect(s1, 0, 0, 6.4, 7.5, LIGHT_BG)
# cyan vertical stripe
add_rect(s1, 6.3, 0, 0.1, 7.5, ACCENT)

# logo / icon placeholder
add_rect(s1, 0.5, 1.1, 1.1, 1.1, ACCENT)
add_text(s1, "⚡", 0.52, 1.05, 1.0, 1.1,
         size=40, bold=True, colour=DARK_BG, align=PP_ALIGN.CENTER)

add_text(s1, "ANTIGRAVITY", 1.8, 1.15, 4.2, 0.65,
         size=38, bold=True, colour=WHITE)
add_text(s1, "ORCHESTRATOR", 1.8, 1.8, 4.2, 0.65,
         size=38, bold=True, colour=ACCENT)
add_text(s1, "Multi-Agent AI Verification System", 0.5, 2.7, 5.6, 0.5,
         size=16, colour=MID_GRAY)
add_text(s1, "Eliminating AI Hallucinations Through\nAutonomous Agent Collaboration",
         0.5, 3.3, 5.6, 0.9, size=13, colour=MID_GRAY, italic=True)

# right side tags
tags = [
    ("🔍 Hallucination Detection", 6.8, 1.5),
    ("✅ Independent Verification", 6.8, 2.4),
    ("🔄 Self-Correction Engine",  6.8, 3.3),
    ("🧠 Evidence-Grounded AI",    6.8, 4.2),
    ("🚀 Real-Time Streaming",     6.8, 5.1),
]
for label, lx, ly in tags:
    add_rect(s1, lx, ly, 5.8, 0.58, CARD_BG)
    add_text(s1, label, lx+0.2, ly+0.08, 5.4, 0.45,
             size=15, bold=True, colour=WHITE)

add_text(s1, "MBU Hackathon 2026  |  Team Antigravity",
         0.5, 6.85, 6, 0.4, size=11, colour=ACCENT)

# ══════════════════════════════════════════════════════════════
#  SLIDE 2 — PROBLEM & SOLUTION
# ══════════════════════════════════════════════════════════════
s2 = blank_slide()
solid_bg(s2, DARK_BG)
header_bar(s2, "The Problem & Our Solution",
           "Why Single-Agent LLMs Fail — And How We Fix It")

# LEFT — problem
add_rect(s2, 0.3, 1.6, 6.0, 5.5, RGBColor(0x2C,0x10,0x10))
add_text(s2, "❌  The Problem with Standard LLMs", 0.5, 1.7, 5.6, 0.45,
         size=15, bold=True, colour=RED)
problems = [
    "Hallucinate facts confidently",
    "Cannot verify their own output",
    "No self-correction capability",
    "Fail on multi-step complex tasks",
    "Ignore contradictions in reasoning",
]
y = 2.2
for p in problems:
    add_text(s2, f"•  {p}", 0.55, y, 5.5, 0.36, size=13, colour=RGBColor(0xFF,0xAA,0xAA))
    y += 0.4

# RIGHT — solution
add_rect(s2, 6.7, 1.6, 6.0, 5.5, RGBColor(0x0A,0x2A,0x1E))
add_text(s2, "✅  Our Multi-Agent Solution", 6.9, 1.7, 5.6, 0.45,
         size=15, bold=True, colour=GREEN)
solutions = [
    "5-stage autonomous pipeline",
    "Independent Verifier cross-checks facts",
    "Critic agent detects logic flaws",
    "Auto-refinement loop corrects errors",
    "Evidence-grounded final output",
]
y = 2.2
for sol in solutions:
    add_text(s2, f"•  {sol}", 6.9, y, 5.5, 0.36, size=13, colour=RGBColor(0xAA,0xFF,0xCC))
    y += 0.4

add_text(s2, "VS", 6.05, 3.8, 0.7, 0.5, size=22, bold=True,
         colour=GOLD, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
#  SLIDE 3 — HOW IT WORKS  (Pipeline diagram)
# ══════════════════════════════════════════════════════════════
s3 = blank_slide()
solid_bg(s3, DARK_BG)
header_bar(s3, "How It Works — Agent Pipeline",
           "A 5-Stage Autonomous Verification Workflow")

agents = [
    ("🗺️", "PLANNER",    "Decomposes the task into 3 structured logical steps",      ACCENT),
    ("🔬", "RESEARCHER", "Gathers evidence-grounded facts (max 5 bullet summary)",    PURPLE),
    ("✍️", "CODER",      "Drafts the response in clean, structured Markdown",         GOLD),
    ("🔍", "VERIFIER",   "Independently cross-checks draft facts vs. research data",  GREEN),
    ("⚖️", "CRITIC",     "Detects hallucinations, contradictions & unsupported claims",RED),
]

xs = [0.25, 2.75, 5.25, 7.75, 10.25]
bw = 2.28

for i, (icon, name, desc, col) in enumerate(agents):
    x = xs[i]
    # card
    add_rect(s3, x, 1.6, bw, 3.8, CARD_BG)
    # top accent bar
    add_rect(s3, x, 1.6, bw, 0.12, col)
    # icon circle
    add_text(s3, icon, x+0.55, 1.75, 1.1, 0.9,
             size=30, align=PP_ALIGN.CENTER)
    add_text(s3, name, x, 2.65, bw, 0.45,
             size=13, bold=True, colour=col, align=PP_ALIGN.CENTER)
    add_text(s3, desc, x+0.1, 3.15, bw-0.2, 1.7,
             size=10.5, colour=MID_GRAY, align=PP_ALIGN.CENTER)

    # arrow between cards
    if i < 4:
        add_text(s3, "→", x+bw+0.01, 2.85, 0.42, 0.45,
                 size=22, bold=True, colour=ACCENT, align=PP_ALIGN.CENTER)

# Refinement loop label
add_rect(s3, 4.8, 5.55, 3.7, 0.5, RGBColor(0x2A,0x1A,0x40))
add_text(s3, "🔄  Auto-Refinement Loop: Critic → Coder (max 1 retry)",
         5.0, 5.6, 3.3, 0.4, size=11, bold=True, colour=PURPLE, align=PP_ALIGN.CENTER)

# Finalizer
add_rect(s3, 4.67, 6.2, 3.95, 0.75, RGBColor(0x0A,0x25,0x1A))
add_text(s3, "✅  FINALIZER — Delivers verified output (or warns with draft)",
         4.87, 6.27, 3.55, 0.55, size=12, bold=True, colour=GREEN, align=PP_ALIGN.CENTER)

# ══════════════════════════════════════════════════════════════
#  SLIDE 4 — JUDGING CRITERIA ALIGNMENT
# ══════════════════════════════════════════════════════════════
s4 = blank_slide()
solid_bg(s4, DARK_BG)
header_bar(s4, "Meeting Every Judging Criterion",
           "How Each Feature Maps Directly to the Evaluation Rubric")

criteria = [
    (ACCENT,  "Hallucination / Error Detection",
               "Critic agent scans for factual errors, confident guesses & contradictions before output is shown"),
    (GREEN,   "Independent Verification",
               "Verifier runs separately on a different model (gpt-oss-20b) — completely isolated from the Coder's reasoning"),
    (GOLD,    "Evidence-Grounded Reasoning",
               "Researcher produces a 5-point evidence summary; Coder can ONLY write what is in that evidence"),
    (PURPLE,  "Contradiction & Unsupported-Claim Detection",
               "Critic prompt explicitly looks for logic gaps and makes the Coder rewrite if found"),
    (RGBColor(0xFF,0x79,0x00), "Self-Correction Effectiveness",
               "Automatic refinement loop: Critic → Coder rewrite → Verifier re-check, all without human input"),
    (RGBColor(0x00,0xD4,0xAA), "Reliability Under Ambiguity",
               "Finalizer never returns a blank page — it always delivers a result with a transparent warning badge"),
]

cols = [(0.25, 0), (4.58, 0), (8.9, 0)]
rows = [(1.58, 2.7), (4.05, 5.15)]

idx = 0
for row_start, row_end in rows:
    for col_start, _ in cols:
        if idx >= len(criteria): break
        col, title, body = criteria[idx]
        bx, by = col_start, row_start
        add_rect(s4, bx, by, 4.08, 2.28, CARD_BG)
        add_rect(s4, bx, by, 4.08, 0.1, col)
        add_text(s4, title, bx+0.15, by+0.15, 3.78, 0.42,
                 size=12, bold=True, colour=col)
        add_text(s4, body, bx+0.15, by+0.6, 3.78, 1.55,
                 size=10.5, colour=MID_GRAY)
        idx += 1

# Innovation badge
add_rect(s4, 0.25, 7.0, 12.83, 0.38, RGBColor(0x1A,0x1A,0x40))
add_text(s4, "🚀  Innovation in Multi-Agent Reasoning: Dual-model smart routing — cheap fast models for verification, powerful model for writing — saving 60% token cost",
         0.45, 7.03, 12.4, 0.32, size=10.5, colour=GOLD)

# ══════════════════════════════════════════════════════════════
#  SLIDE 5 — TECH STACK & ADDITIONAL FEATURES
# ══════════════════════════════════════════════════════════════
s5 = blank_slide()
solid_bg(s5, DARK_BG)
header_bar(s5, "Technology Stack & Additional Features",
           "Built for Scale, Speed, and Reliability")

# Backend card
add_bullet_box(s5,
    ["Flask (Python) — REST API + SSE streaming",
     "Custom API Router — Hackathon's gpt-oss endpoint",
     "Dual-model routing: gpt-oss-120b (Writer), gpt-oss-20b (Verifier/Critic)",
     "Auto-retry + graceful fallback on 429 rate limits",
     "TypedDict state machine — shared memory across agents"],
    left=0.3, top=1.6, width=6.0, height=3.5,
    title="⚙️  Backend", title_colour=ACCENT, body_size=11.5)

# Frontend card
add_bullet_box(s5,
    ["Next.js + React — full SSR web app",
     "Tailwind CSS — premium light-mode design system",
     "react-markdown + remark-gfm — safe Markdown rendering",
     "Server-Sent Events (SSE) — real-time audit trail streaming",
     "Collapsible agent log sidebar — full transparency"],
    left=6.7, top=1.6, width=6.0, height=3.5,
    title="🎨  Frontend", title_colour=GOLD, body_size=11.5)

# Additional features strip
features = [
    ("🛡️", "Fault Tolerance", "Never crashes — always returns a result"),
    ("⚡", "Smart Routing",   "60% token savings via model tiering"),
    ("📡", "Live Streaming",  "Real-time agent progress visible to user"),
    ("📝", "Audit Trail",     "Every agent's reasoning is logged & shown"),
]
add_rect(s5, 0.3, 5.3, 12.73, 0.38, LIGHT_BG)
add_text(s5, "✨  ADDITIONAL FEATURES", 0.5, 5.33, 5, 0.3,
         size=12, bold=True, colour=ACCENT)

fx = [0.3, 3.5, 6.7, 9.9]
for i, (icon, label, desc) in enumerate(features):
    add_rect(s5, fx[i], 5.82, 3.0, 1.5, CARD_BG)
    add_text(s5, f"{icon}  {label}", fx[i]+0.15, 5.9, 2.7, 0.4,
             size=12, bold=True, colour=GOLD)
    add_text(s5, desc, fx[i]+0.15, 6.35, 2.7, 0.75, size=10.5, colour=MID_GRAY)

# ══════════════════════════════════════════════════════════════
#  SLIDE 6 — TEAM
# ══════════════════════════════════════════════════════════════
s6 = blank_slide()
solid_bg(s6, DARK_BG)
# centre glow
add_rect(s6, 3.17, 0.8, 7.0, 6.0, LIGHT_BG)

add_text(s6, "⚡", 5.9, 1.0, 1.5, 1.0, size=50, bold=True, colour=ACCENT, align=PP_ALIGN.CENTER)
add_text(s6, "TEAM ANTIGRAVITY", 0.3, 2.1, 12.73, 0.75,
         size=36, bold=True, colour=WHITE, align=PP_ALIGN.CENTER)
add_text(s6, "MBU Hackathon  2026", 0.3, 2.85, 12.73, 0.45,
         size=16, colour=ACCENT, align=PP_ALIGN.CENTER)

# cyan divider
add_rect(s6, 4.5, 3.45, 4.33, 0.06, ACCENT)

# TODO — replace with real names
names = [
    "Member 1 Name  |  Roll No.",
    "Member 2 Name  |  Roll No.",
    "Member 3 Name  |  Roll No.",
    "Member 4 Name  |  Roll No.",
]
y = 3.65
for name in names:
    add_text(s6, name, 0.3, y, 12.73, 0.5,
             size=17, colour=MID_GRAY, align=PP_ALIGN.CENTER)
    y += 0.58

add_text(s6, "\"The future of AI isn't one giant model;\nit's a swarm of specialized agents working together.\"",
         1.0, 6.05, 11.33, 0.9,
         size=13, italic=True, colour=GOLD, align=PP_ALIGN.CENTER)

# ── SAVE ─────────────────────────────────────────────────────
out_path = r"c:\Users\nerli\Desktop\MBU hackathon\Antigravity_Pitch_Deck_v2.pptx"
prs.save(out_path)
print(f"SAVED: {out_path}")
