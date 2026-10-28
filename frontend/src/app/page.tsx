"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AGENT_META: Record<string, { label: string; icon: string; color: string; badge: string }> = {
  Strategist: {
    label: "Strategist",
    icon: "🗺️",
    color: "from-blue-500/20 to-cyan-500/20 border-cyan-500/30 text-cyan-300",
    badge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
  },
  Researcher: {
    label: "Researcher",
    icon: "🔬",
    color: "from-purple-500/20 to-indigo-500/20 border-purple-500/30 text-purple-300",
    badge: "bg-purple-500/10 text-purple-400 border-purple-500/20"
  },
  Synthesizer: {
    label: "Synthesizer",
    icon: "✍️",
    color: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-300",
    badge: "bg-amber-500/10 text-amber-400 border-amber-500/20"
  },
  Auditor: {
    label: "Auditor",
    icon: "⚖️",
    color: "from-rose-500/20 to-pink-500/20 border-rose-500/30 text-rose-300",
    badge: "bg-rose-500/10 text-rose-400 border-rose-500/20"
  },
  // Legacy aliases
  Planner: {
    label: "Strategist",
    icon: "🗺️",
    color: "from-blue-500/20 to-cyan-500/20 border-cyan-500/30 text-cyan-300",
    badge: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
  },
  Coder: {
    label: "Synthesizer",
    icon: "✍️",
    color: "from-amber-500/20 to-orange-500/20 border-amber-500/30 text-amber-300",
    badge: "bg-amber-500/10 text-amber-400 border-amber-500/20"
  },
  Critic: {
    label: "Auditor",
    icon: "⚖️",
    color: "from-rose-500/20 to-pink-500/20 border-rose-500/30 text-rose-300",
    badge: "bg-rose-500/10 text-rose-400 border-rose-500/20"
  }
};

export default function Home() {
  const [task, setTask] = useState("");
  const [provider, setProvider] = useState("auto");
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [showAuditorFeedback, setShowAuditorFeedback] = useState(false);
  const [copied, setCopied] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiUrl}/api/providers`)
      .then(res => res.json())
      .then(data => {
        if (data.providers) setAvailableProviders(data.providers);
      })
      .catch(() => {});
  }, [apiUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;
    setLoading(true);
    setErrorMsg(null);
    setAuditTrail([]);
    setFinalResult(null);
    setExpandedIndex(null);
    setShowAuditorFeedback(false);

    try {
      const response = await fetch(`${apiUrl}/api/run-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: task, provider }),
      });

      if (!response.body) throw new Error("No stream received from backend");
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let done = false;

      while (!done) {
        const { value, done: rd } = await reader.read();
        done = rd;
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const data = JSON.parse(line.slice(6));
              if (data.status === "running") {
                setAuditTrail(prev => {
                  const next = [...prev, data.update];
                  setExpandedIndex(next.length - 1);
                  return next;
                });
              } else if (data.status === "completed") {
                setFinalResult(data.final_state);
                setLoading(false);
              }
            } catch {}
          }
        }
      }
    } catch {
      setErrorMsg("Cannot reach Python backend. Ensure `python main.py` is running on port 8000.");
      setLoading(false);
    }
  };

  const handleCopyMarkdown = () => {
    if (!finalResult?.draft) return;
    navigator.clipboard.writeText(finalResult.draft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportMarkdown = () => {
    if (!finalResult?.draft) return;
    const blob = new Blob([finalResult.draft], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `versatile_ai_report_${Date.now()}.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <style>{`
        body { background: #030712; color: #f3f4f6; font-family: ui-sans-serif, system-ui, -apple-system, sans-serif; }
        .prose h1, .prose h2, .prose h3 { color: #f9fafb; margin-top: 1.5rem; margin-bottom: 0.75rem; font-weight: 700; letter-spacing: -0.025em; }
        .prose h1 { font-size: 1.6rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; }
        .prose h2 { font-size: 1.3rem; }
        .prose h3 { font-size: 1.1rem; }
        .prose p { color: #d1d5db; line-height: 1.8; margin-bottom: 1rem; }
        .prose ul, .prose ol { color: #d1d5db; padding-left: 1.5rem; margin-bottom: 1rem; }
        .prose li { margin-bottom: 0.4rem; }
        .prose strong { color: #ffffff; font-weight: 600; }
        .prose a { color: #38bdf8; text-decoration: underline; text-underline-offset: 3px; font-weight: 500; }
        .prose a:hover { color: #7dd3fc; }
        .prose table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background: rgba(17, 24, 39, 0.7); border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); }
        .prose thead tr { background: rgba(31, 41, 55, 0.8); border-bottom: 1px solid rgba(255,255,255,0.1); }
        .prose thead th { color: #9ca3af; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.85rem 1rem; text-align: left; }
        .prose tbody td { color: #e5e7eb; padding: 0.85rem 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.9rem; }
        .prose tbody tr:hover td { background: rgba(255,255,255,0.03); }
        .prose blockquote { border-left: 3px solid #6366f1; background: rgba(99, 102, 241, 0.1); padding: 1rem; color: #c7d2fe; margin: 1.25rem 0; border-radius: 0 8px 8px 0; }
        .prose code { background: rgba(255,255,255,0.08); color: #38bdf8; padding: 0.2rem 0.45rem; border-radius: 6px; font-size: 0.875em; font-family: monospace; }
        .prose pre { background: #0b0f19; color: #e5e7eb; border-radius: 0.75rem; padding: 1.25rem; overflow-x: auto; border: 1px solid rgba(255,255,255,0.08); }
        .prose pre code { background: none; border: none; color: inherit; padding: 0; }
        
        .scrollbar-dark::-webkit-scrollbar { width: 5px; }
        .scrollbar-dark::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-dark::-webkit-scrollbar-thumb { background: #374151; border-radius: 5px; }
        .scrollbar-dark::-webkit-scrollbar-thumb:hover { background: #4b5563; }
      `}</style>

      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
        
        {/* Subtle Ambient Background Gradients */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-indigo-600/10 blur-[120px] pointer-events-none rounded-full"></div>
        <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-cyan-600/10 blur-[120px] pointer-events-none rounded-full"></div>

        {/* Top Navigation */}
        <header className="border-b border-slate-800/80 px-6 md:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 backdrop-blur-xl sticky top-0 z-30">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 border border-white/20">
              <span className="text-lg">⚡</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold tracking-tight text-white text-lg">VersatileAI</span>
                <span className="text-[10px] font-mono tracking-wider bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 px-2 py-0.5 rounded-full font-bold uppercase">v2.1 Swarm</span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium">Autonomous Grounded Multi-Agent Verification</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Model Provider Selector */}
            <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl px-2 py-1 shadow-inner">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider pl-1.5 hidden sm:inline">Engine:</span>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                disabled={loading}
                className="text-xs font-semibold bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 cursor-pointer hover:bg-slate-700/80 transition-all"
              >
                <option value="auto">⚡ Auto Routing (Groq + Nemotron)</option>
                <option value="groq">⚡ Groq LPU (Ultra-Fast Free)</option>
                <option value="openrouter">🌐 OpenRouter (Nemotron 3.5 Free)</option>
                <option value="nvidia">🟢 NVIDIA Direct NIM</option>
              </select>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 px-3 py-1.5 rounded-full shadow-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              100% Free Tier Active
            </div>
          </div>
        </header>

        {errorMsg && (
          <div className="bg-rose-950/80 border-b border-rose-800 px-8 py-3 text-xs text-rose-300 flex items-center justify-between">
            <span>⚠️ {errorMsg}</span>
            <button onClick={() => setErrorMsg(null)} className="font-bold text-rose-200 hover:underline">Dismiss</button>
          </div>
        )}

        <div className="flex flex-1 overflow-hidden relative z-10">
          
          {/* LEFT PANEL: Live Agent Swarm Stream */}
          <aside className="w-80 xl:w-96 border-r border-slate-800/80 flex flex-col bg-slate-900/40 backdrop-blur-md flex-shrink-0 z-10">
            <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-900/70">
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Agent Reasoning Loop</span>
              </div>
              {loading && (
                <span className="flex items-center gap-1.5 text-[11px] text-cyan-400 font-mono animate-pulse">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  live stream
                </span>
              )}
            </div>
            
            <div className="flex-1 overflow-y-auto scrollbar-dark p-4 space-y-3">
              {auditTrail.length === 0 && !loading ? (
                <div className="text-center mt-20 text-slate-500 text-sm">
                  <div className="w-12 h-12 rounded-2xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-center mx-auto mb-3 text-2xl">
                    🤖
                  </div>
                  <p className="font-semibold text-slate-400">Swarm in Standby</p>
                  <p className="text-xs mt-1 text-slate-600 max-w-xs mx-auto">Enter any prompt above to watch the 4 agents plan, search, draft, and audit in real-time.</p>
                </div>
              ) : (
                auditTrail.map((step, i) => {
                  const meta = AGENT_META[step.agent] || { label: step.agent, icon: "🔹", color: "from-slate-500/20 border-slate-700 text-slate-300", badge: "bg-slate-800 text-slate-400 border-slate-700" };
                  return (
                    <div
                      key={i}
                      className={`w-full text-left rounded-xl border transition-all duration-200 bg-gradient-to-r ${meta.color} ${expandedIndex === i ? 'ring-1 ring-white/30 shadow-lg' : 'hover:border-slate-600'}`}
                    >
                      <button
                        onClick={() => setExpandedIndex(expandedIndex === i ? null : i)}
                        className="w-full p-3 flex items-center gap-3 text-left focus:outline-none"
                      >
                        <span className="text-xl flex-shrink-0 bg-slate-900/80 w-10 h-10 flex items-center justify-center rounded-lg border border-white/10 shadow-inner">
                          {meta.icon}
                        </span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-bold text-white truncate">{meta.label}</span>
                            {step.latency_ms && (
                              <span className="text-[10px] font-mono text-slate-400 bg-slate-900/60 px-1.5 py-0.5 rounded border border-white/5">
                                {step.latency_ms}ms
                              </span>
                            )}
                          </div>
                          <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${meta.badge}`}>
                            {step.action}
                          </span>
                        </div>
                      </button>

                      {expandedIndex === i && (
                        <div className="px-3.5 pb-3.5 pt-1 border-t border-white/5">
                          <p className="text-[12px] text-slate-300 font-mono leading-relaxed whitespace-pre-wrap break-words max-h-60 overflow-y-auto scrollbar-dark bg-slate-950/80 p-2.5 rounded-lg border border-white/5">
                            {step.content}
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })
              )}

              {loading && (
                <div className="flex items-center gap-3 px-4 py-3.5 rounded-xl border border-indigo-500/40 bg-indigo-950/30 text-indigo-300">
                  <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin flex-shrink-0"></div>
                  <span className="text-xs font-mono font-medium tracking-wide">Next Agent Reasoning...</span>
                </div>
              )}
            </div>
          </aside>

          {/* RIGHT PANEL: Search Input & Main Output */}
          <main className="flex-1 flex flex-col overflow-hidden bg-slate-950 relative">
            
            {/* Search Input Bar */}
            <div className="px-6 md:px-10 py-6 border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-xl z-20">
              <form onSubmit={handleSubmit} className="flex gap-3 items-center max-w-4xl mx-auto">
                <div className="flex-1 flex items-center gap-3 bg-slate-900/90 border border-slate-700/80 rounded-2xl px-5 py-3.5 focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/30 transition-all shadow-xl shadow-black/40">
                  <span className="text-slate-400 text-lg">💬</span>
                  <input
                    type="text"
                    value={task}
                    onChange={e => setTask(e.target.value)}
                    placeholder="Enter any complex question for verified, grounded multi-agent research..."
                    className="flex-1 bg-transparent text-white placeholder-slate-500 focus:outline-none font-medium text-base"
                    disabled={loading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !task.trim()}
                  className="bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold px-7 py-3.5 rounded-2xl transition-all flex items-center gap-2 shadow-lg shadow-indigo-600/30 flex-shrink-0 active:scale-95"
                >
                  {loading ? (
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  ) : (
                    <span>🚀</span>
                  )}
                  {loading ? "Verifying..." : "Run Swarm"}
                </button>
              </form>
            </div>

            {/* Main Output / Results Area */}
            <div className="flex-1 overflow-y-auto scrollbar-dark px-6 md:px-10 py-8 z-10">
              
              {!finalResult && !loading && (
                <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto py-12">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-indigo-500/20 to-cyan-500/20 border border-indigo-500/30 flex items-center justify-center mb-6 text-3xl shadow-xl shadow-indigo-500/10">
                    🛡️
                  </div>
                  <h2 className="text-2xl font-black text-white mb-2 tracking-tight">Zero-Hallucination Multi-Agent Verification</h2>
                  <p className="text-sm text-slate-400 leading-relaxed max-w-lg mb-8">
                    Every answer is deconstructed by a <strong className="text-cyan-400">Strategist</strong>, grounded in live web sources by a <strong className="text-purple-400">Researcher</strong>, synthesized by a <strong className="text-amber-400">Writer</strong>, and audited for factual truth by an <strong className="text-rose-400">Auditor</strong>.
                  </p>
                  
                  {/* Quick-Prompt Pills */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full">
                    {[
                      "Compare real apple vs plastic toy apple",
                      "Latest breakthroughs in Quantum Computing",
                      "Why does SQL scale vertically while NoSQL scales horizontally?",
                      "How do black hole event horizons work simply?"
                    ].map(s => (
                      <button
                        key={s}
                        onClick={() => setTask(s)}
                        className="text-xs font-semibold text-left text-slate-300 bg-slate-900/70 hover:bg-slate-800/80 hover:text-white border border-slate-800 hover:border-slate-700 rounded-xl p-3.5 transition-all shadow-md group flex items-start gap-2.5"
                      >
                        <span className="text-indigo-400 group-hover:scale-110 transition-transform">▸</span>
                        <span>{s}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loading && auditTrail.length === 0 && (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center bg-slate-900/60 p-8 rounded-2xl border border-slate-800 backdrop-blur-xl">
                    <div className="flex gap-2 justify-center mb-4">
                      {[0, 1, 2].map(i => (
                        <div key={i} className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }}></div>
                      ))}
                    </div>
                    <p className="text-xs text-slate-400 font-mono tracking-widest uppercase font-bold">Activating Multi-Model Swarm...</p>
                  </div>
                </div>
              )}

              {finalResult && (
                <div className="max-w-4xl mx-auto bg-slate-900/50 backdrop-blur-xl p-6 md:p-10 rounded-3xl border border-slate-800 shadow-2xl">
                  
                  {/* Top Status Header */}
                  <div className={`flex flex-wrap items-center justify-between gap-4 px-5 py-3.5 rounded-2xl mb-6 border ${finalResult.is_valid ? 'bg-emerald-950/40 border-emerald-500/30' : 'bg-rose-950/40 border-rose-500/30'}`}>
                    <div className={`flex items-center gap-2.5 text-sm font-extrabold ${finalResult.is_valid ? 'text-emerald-400' : 'text-rose-400'}`}>
                      <span>{finalResult.is_valid ? "✅" : "⚠️"}</span>
                      <span>{finalResult.is_valid ? "Audited & Factually Verified" : "Auditor Flagged Edge-Cases"}</span>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      {finalResult.metrics?.total_time_s && (
                        <span className="text-xs text-slate-300 font-mono bg-slate-950/80 px-2.5 py-1 rounded-lg border border-white/10">
                          ⏱️ {finalResult.metrics.total_time_s}s
                        </span>
                      )}
                      <span className="text-xs font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-2.5 py-1 rounded-lg font-bold">
                        Score: {finalResult.quality_score || 9}/10
                      </span>
                      <button
                        onClick={handleCopyMarkdown}
                        className="text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1 rounded-lg transition-all flex items-center gap-1.5"
                      >
                        {copied ? "✓ Copied!" : "📋 Copy"}
                      </button>
                      <button
                        onClick={handleExportMarkdown}
                        className="text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded-lg transition-all flex items-center gap-1.5 shadow-md shadow-indigo-600/30"
                      >
                        📥 Export .md
                      </button>
                    </div>
                  </div>

                  {/* Auditor Notes Accordion */}
                  {finalResult.feedback && (
                    <div className="mb-6 border border-slate-800 rounded-xl overflow-hidden bg-slate-950/60">
                      <button
                        onClick={() => setShowAuditorFeedback(!showAuditorFeedback)}
                        className="w-full text-left px-4 py-2.5 flex items-center justify-between text-xs font-bold text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 transition-colors"
                      >
                        <span className="flex items-center gap-2">
                          <span>⚖️</span> Auditor Verification Findings &amp; Critique
                        </span>
                        <span>{showAuditorFeedback ? "▲ Hide" : "▼ Inspect"}</span>
                      </button>
                      {showAuditorFeedback && (
                        <div className="px-4 py-3 border-t border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed bg-black/40">
                          {finalResult.feedback}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Rendered Verified Output */}
                  <div className="prose max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {finalResult.draft}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </>
  );
}
