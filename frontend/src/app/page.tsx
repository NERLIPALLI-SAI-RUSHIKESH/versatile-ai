"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AGENT_COLORS: Record<string, string> = {
  Planner: "bg-blue-50 text-blue-600 border-blue-200",
  Researcher: "bg-purple-50 text-purple-600 border-purple-200",
  Coder: "bg-amber-50 text-amber-600 border-amber-200",
  Verifier: "bg-cyan-50 text-cyan-600 border-cyan-200",
  Critic: "bg-rose-50 text-rose-600 border-rose-200",
  Finalizer: "bg-emerald-50 text-emerald-600 border-emerald-200",
};

const AGENT_ICONS: Record<string, string> = {
  Planner: "🗺️",
  Researcher: "🔬",
  Coder: "✍️",
  Verifier: "🔍",
  Critic: "⚖️",
  Finalizer: "✅",
};

export default function Home() {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const [auditTrail, setAuditTrail] = useState<any[]>([]);
  const [finalResult, setFinalResult] = useState<any>(null);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) return;
    setLoading(true);
    setAuditTrail([]);
    setFinalResult(null);
    setExpandedIndex(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/run-task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: task }),
      });
      if (!response.body) throw new Error("No stream");
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
      alert("Cannot connect to backend. Make sure Python server is running on port 8000.");
      setLoading(false);
    }
  };

  return (
    <>
      <style>{`
        body { background: #f8fafc; }
        .prose h1,h2,h3 { color: #0f172a; margin-top: 1.5rem; margin-bottom: 0.75rem; font-weight: 700; }
        .prose p { color: #334155; line-height: 1.8; }
        .prose ul { color: #475569; padding-left: 1.5rem; }
        .prose li { margin-bottom: 0.4rem; }
        .prose strong { color: #0f172a; font-weight: 600; }
        .prose table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .prose thead tr { border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
        .prose thead th { color: #475569; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 1rem; text-align: left; }
        .prose tbody td { color: #334155; padding: 1rem; border-bottom: 1px solid #f1f5f9; font-size: 0.9rem; }
        .prose tbody tr:hover td { background: #f8fafc; }
        .prose blockquote { border-left: 4px solid #3b82f6; background: #eff6ff; padding: 1rem; color: #1e3a8a; margin: 1rem 0; border-radius: 0 8px 8px 0; }
        .prose code { background: #f1f5f9; color: #0f172a; padding: 0.2rem 0.4rem; border-radius: 4px; font-size: 0.875em; border: 1px solid #e2e8f0; }
        .prose pre { background: #0f172a; color: #e2e8f0; border-radius: 0.5rem; padding: 1.25rem; overflow-x: auto; }
        .prose pre code { background: none; border: none; color: inherit; padding: 0; }
        .prose hr { border-color: #e2e8f0; margin: 2rem 0; }
        
        .scrollbar-thin::-webkit-scrollbar { width: 5px; }
        .scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
        .scrollbar-thin::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 5px; }
        .scrollbar-thin::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
      `}</style>

      <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col">
        
        {/* Top Nav */}
        <header className="border-b border-slate-200 px-8 py-4 flex items-center justify-between bg-white/80 backdrop-blur-xl sticky top-0 z-10 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-200">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <span className="font-bold text-slate-900 tracking-tight text-lg">VersatileAI</span>
            <span className="text-[11px] text-slate-500 font-mono bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">v2.0</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-emerald-600 font-mono bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Groq LPU Online
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          
          {/* LEFT PANEL: Agent logs */}
          <aside className="w-80 xl:w-96 border-r border-slate-200 flex flex-col bg-white flex-shrink-0 shadow-[4px_0_24px_rgba(0,0,0,0.02)] z-0">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Agent Pipeline</span>
              {loading && <span className="text-[10px] text-indigo-500 font-mono animate-pulse font-semibold">streaming...</span>}
            </div>
            
            <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3 bg-slate-50/30">
              {auditTrail.length === 0 && !loading ? (
                <div className="text-center mt-16 text-slate-400 text-sm font-mono">
                  <p className="text-4xl mb-3 opacity-50">🤖</p>
                  <p className="font-semibold text-slate-500">System idle</p>
                  <p className="text-xs mt-1 text-slate-400">Awaiting task initialization.</p>
                </div>
              ) : (
                auditTrail.map((step, i) => (
                  <button
                    key={i}
                    onClick={() => setExpandedIndex(expandedIndex === i ? null : i)}
                    className={`w-full text-left rounded-xl border transition-all duration-200 shadow-sm ${expandedIndex === i ? 'bg-white border-indigo-200 ring-2 ring-indigo-50' : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow'}`}
                  >
                    <div className="p-3.5 flex items-center gap-3">
                      <span className="text-xl flex-shrink-0 bg-slate-50 w-10 h-10 flex items-center justify-center rounded-lg border border-slate-100">{AGENT_ICONS[step.agent] || "🔹"}</span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-bold text-slate-800 truncate">{step.agent}</span>
                          <svg className={`w-4 h-4 text-slate-400 flex-shrink-0 transition-transform ${expandedIndex === i ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                        </div>
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${AGENT_COLORS[step.agent] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                          {step.action}
                        </span>
                      </div>
                    </div>
                    {expandedIndex === i && (
                      <div className="px-4 pb-4 pt-2 border-t border-slate-100 bg-slate-50/50 rounded-b-xl">
                        <p className="text-[12px] text-slate-600 font-mono leading-relaxed whitespace-pre-wrap break-words max-h-60 overflow-y-auto scrollbar-thin mt-2">
                          {step.content}
                        </p>
                      </div>
                    )}
                  </button>
                ))
              )}
              {loading && (
                <div className="flex items-center gap-3 px-4 py-3.5 rounded-xl border border-indigo-200 bg-indigo-50 shadow-sm">
                  <svg className="animate-spin w-5 h-5 text-indigo-600 flex-shrink-0" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  <span className="text-xs text-indigo-700 font-bold font-mono tracking-wide">Agent processing...</span>
                </div>
              )}
            </div>
          </aside>

          {/* RIGHT PANEL: Main content */}
          <main className="flex-1 flex flex-col overflow-hidden bg-slate-50 relative">
            {/* Subtle background pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none"></div>

            {/* Input bar */}
            <div className="px-8 py-6 border-b border-slate-200 bg-white/80 backdrop-blur-md z-10 shadow-sm">
              <form onSubmit={handleSubmit} className="flex gap-3 items-center max-w-5xl mx-auto">
                <div className="flex-1 flex items-center gap-3 bg-white border border-slate-300 rounded-xl px-5 py-3.5 focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all shadow-sm">
                  <svg className="w-5 h-5 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
                  <input
                    type="text"
                    value={task}
                    onChange={e => setTask(e.target.value)}
                    placeholder="Describe your task for the agent swarm..."
                    className="flex-1 bg-transparent text-slate-800 placeholder-slate-400 focus:outline-none font-medium text-base"
                    disabled={loading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || !task.trim()}
                  className="bg-slate-900 hover:bg-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold px-8 py-3.5 rounded-xl transition-all flex items-center gap-2 shadow-lg shadow-slate-200 flex-shrink-0"
                >
                  {loading ? (
                    <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  )}
                  {loading ? "Running" : "Deploy Swarm"}
                </button>
              </form>
            </div>

            {/* Output area */}
            <div className="flex-1 overflow-y-auto scrollbar-thin px-8 py-10 z-10">
              {!finalResult && !loading && (
                <div className="h-full flex flex-col items-center justify-center text-center max-w-xl mx-auto bg-white p-12 rounded-3xl border border-slate-200 shadow-xl shadow-slate-200/40">
                  <div className="w-20 h-20 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center mb-6 shadow-sm">
                    <svg className="w-10 h-10 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" /></svg>
                  </div>
                  <h2 className="text-2xl font-extrabold text-slate-900 mb-3 tracking-tight">Multi-Agent Verification Engine</h2>
                  <p className="text-base text-slate-500 leading-relaxed font-medium">Enter a complex task above. A swarm of specialized AI agents will plan, research, write, verify, and critique the output before delivering a final result.</p>
                  
                  <div className="mt-10 grid grid-cols-2 gap-3 w-full">
                    {["Plan a trip to Goa under ₹10,000", "Explain Quantum Computing simply", "Write a Python web scraper", "Compare Next.js vs React"].map(s => (
                      <button key={s} onClick={() => setTask(s)} className="text-sm font-medium text-left text-slate-600 bg-slate-50 hover:bg-indigo-50 hover:text-indigo-700 border border-slate-200 hover:border-indigo-200 rounded-xl p-4 transition-all shadow-sm">
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loading && auditTrail.length === 0 && (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                    <div className="flex gap-2 justify-center mb-5">
                      {[0,1,2].map(i => <div key={i} className="w-3 h-3 rounded-full bg-indigo-500 animate-bounce" style={{animationDelay:`${i*0.15}s`}}></div>)}
                    </div>
                    <p className="text-sm text-slate-500 font-mono font-bold tracking-widest uppercase">Initializing Swarm...</p>
                  </div>
                </div>
              )}

              {finalResult && (
                <div className="max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500 bg-white p-8 md:p-12 rounded-3xl border border-slate-200 shadow-2xl shadow-slate-200/50">
                  {/* Status Bar */}
                  <div className={`flex items-center justify-between px-6 py-4 rounded-xl mb-8 border shadow-sm ${finalResult.is_valid ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}>
                    <div className={`flex items-center gap-3 text-sm font-bold ${finalResult.is_valid ? 'text-emerald-700' : 'text-rose-700'}`}>
                      {finalResult.is_valid ? (
                        <><svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>Output Verified &amp; Approved</>
                      ) : (
                        <><svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>Flagged by Critic (See Warning)</>
                      )}
                    </div>
                    <span className="text-xs text-slate-500 font-mono bg-white px-3 py-1 rounded-md border border-slate-200/50">{finalResult.loop_count} refinement loops</span>
                  </div>

                  {/* Rendered Markdown Output */}
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
