"use client";
import React, { useRef } from "react";

// Server Component: horizontally scrollable, full-viewport examples
// Each card mimics an "XBOW exploit" walkthrough layout: left steps, right code panel
// Uses Tailwind only; no client JS needed

const stepsPreset = [
  { k: "i", title: "Introduction", desc: "Overview and context" },
  { k: "1", title: "Scans Main Page" },
  { k: "2", title: "Finds XSS Vector" },
  { k: "3", title: "Tries Encoded Bypass" },
  { k: "4", title: "Bypasses Filter Logic" },
];

function StepsList() {
  return (
    <div className="w-full min-w-0 sm:max-w-sm sm:shrink-0">
      <div className="space-y-3">
        {stepsPreset.map((s, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 rounded-xl border border-[#e5e8eb] bg-white p-3 transition-all duration-200 hover:shadow-md ${
              i === 0 ? "ring-2 ring-[#4a90e2]/30" : ""
            }`}
          >
            <span className={`inline-flex h-6 w-6 items-center justify-center rounded-md text-xs font-semibold transition-all duration-200 ${
              i === 0
                ? "bg-[#4a90e2] text-white"
                : "bg-black text-white"
            }`}
            >
              {s.k}
            </span>
            <div>
              <div className="text-sm font-medium text-[#2c3e50]">
                {s.title}
              </div>
              {s.desc && (
                <div className="text-xs text-[#7f8c8d]">{s.desc}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CodePanel() {
  return (
    <div className="relative flex self-start max-h-[320px] min-h-0 w-full flex-col overflow-hidden rounded-2xl bg-black text-[12px] text-[#c9d1d9] shadow-lg">
      <div className="flex items-center gap-2 border-b border-white/10 px-4 py-2 text-xs text-white/60">
        <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
        <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
        <span className="h-3 w-3 rounded-full bg-[#27c93f]" />
        <span className="ml-3">index.html</span>
      </div>
      <pre className="flex-1 w-full overflow-auto p-4 leading-6">
{`<link rel="shortcut icon" href="static/assets/fav-icon.ico" />
<link rel="stylesheet" type="text/css" href="static/css/site.css" />
<link rel="stylesheet" type="text/css" href="static/css/theme.css" />
<title>Dalgona Challenges</title>

<!-- Analyst notes -->
// Attempting payload injection via query parameter
// Checking output encoding on innerHTML sinks

<script>
  const p = new URLSearchParams(location.search);
  const q = p.get('q');
  // Vulnerable sink
  document.getElementById('result').innerHTML = q;
</script>`}
      </pre>
      <div className="border-t border-white/10 p-3 text-sm text-white/70">
        We investigate this challenge by inspecting the DOM and identifying unescaped sinks.
      </div>
    </div>
  );
}

const ExploitCard = React.forwardRef<HTMLDivElement, { index: number; title: string; subtitle: string; onClick: () => void }>(
  ({ index, title, subtitle, onClick }, ref) => {
    return (
      <section className="relative flex h-[74vh] w-[88vw] md:w-[72vw] lg:w-[64vw] shrink-0 snap-center items-center justify-center bg-background px-2 py-0">
        <div
          ref={ref}
          onClick={onClick}
          className="mx-auto flex h-full min-h-0 w-full cursor-pointer select-none flex-col overflow-hidden rounded-3xl border border-[#e5e8eb] bg-white px-5 pt-5 pb-3 shadow-lg transition-all duration-500 hover:shadow-xl sm:px-7 sm:pt-7 sm:pb-4"
        >
          <div className="flex items-start justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-black px-3 py-1 text-[10px] font-semibold text-white">
                <span>DEMO example {index + 1}</span>
              </div>
              <h2 className="mt-3 text-2xl font-semibold text-[#2c3e50] sm:text-3xl">
                {title}
              </h2>
              <p className="mt-2 max-w-2xl text-[#7f8c8d] text-sm sm:text-base">{subtitle}</p>
            </div>
            <button
              aria-label="Share"
              className="rounded-xl border border-[#e5e8eb] px-3 py-2 text-sm text-[#7f8c8d] transition-all duration-200 hover:bg-[#f8fafb] hover:shadow-sm"
              onClick={(e) => e.stopPropagation()}
            >
              ⤴
            </button>
          </div>

          <div className="mt-5 grid min-w-0 grid-cols-1 items-start gap-5 md:grid-cols-[260px_1fr]">
            <StepsList />
            <div className="min-w-0">
              <CodePanel />
            </div>
          </div>
        </div>
      </section>
    );
  }
);
ExploitCard.displayName = "ExploitCard";

const cards = [
  {
    title: "Bypassing Filters and Exploiting XSS",
    subtitle:
      "meowBot analyzes the DOM, evaluates sinks/sources, and proposes safe patches while showing a reproducible exploit.",
  },
  {
    title: "Cmd Injection via Misconfig",
    subtitle:
      "Detects shell interpolation risks and demonstrates a minimal PoC with sanitized remediation.",
  },
  {
    title: "SQLi in Legacy ORM Adapter",
    subtitle:
      "Shows taint propagation from request to query build, including prepared-statement migration steps.",
  },
  {
    title: "SSRF Through Image Proxy Service",
    subtitle:
      "Maps internal egress paths and blocks unsafe URL schemes with defense-in-depth policies.",
  },
  {
    title: "Prototype Pollution in Deep Merge",
    subtitle:
      "Explains gadget chain creation and hardens merge semantics against __proto__/constructor tricks.",
  },
  {
    title: "Path Traversal in Zip Extraction",
    subtitle:
      "Demonstrates zip-slip exploitation and introduces hardened extraction with path validation.",
  },
];

export default function Examples() {
  const railRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);

  const handleClickCard = (idx: number) => {
    const el = cardRefs.current[idx];
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
  };

  return (
    <div className="relative z-10 w-full overflow-x-auto overflow-y-visible snap-x snap-mandatory scroll-smooth py-10 [scrollbar-width:none] [-ms-overflow-style:none] [-webkit-overflow-scrolling:touch] hide-scrollbar">
      {/* hide scrollbar in webkit */}
      <style>{`.hide-scrollbar::-webkit-scrollbar{display:none}`}</style>

      {/* gradient edges for peek hint */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-8 bg-gradient-to-r from-background to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-background to-transparent" />
      
      <div ref={railRef} className="hide-scrollbar flex gap-6 px-4 sm:px-6">
        {cards.map((c, i) => (
          <ExploitCard
            key={i}
            index={i}
            title={c.title}
            subtitle={c.subtitle}
            onClick={() => handleClickCard(i)}
            ref={(el) => (cardRefs.current[i] = el)}
          />
        ))}
      </div>
    </div>
  );
}