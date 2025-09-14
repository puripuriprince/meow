import React from "react";
import { CopyButton } from "@/components/ui/copy-button";

const AnalysisFeatures = () => {
  return (
    <section className="pt-20 pb-12 overflow-visible">
      <div className="grid grid-cols-1 items-start gap-10 lg:grid-cols-2">
        {/* Left: Marketing copy */}
        <div className="space-y-6">
          <h2 className="text-4xl font-semibold text-foreground">
            Your terminal-first AI cybersecurity expert
          </h2>
          <p className="text-body-large">
            Pentest without leaving the CLI. EvoSec searches massive attack surfaces,
            explains issues, drafts fixes, and automates debug loops.
          </p>
          <p className="text-body-large">
            Your tools. Your workflow. Zero context switching.
          </p>

          <div className="pt-2">
            <p className="mb-3 text-sm text-muted-foreground">
              Install Node.js 18+, then run:
            </p>
            <div className="inline-flex items-center rounded-full border border-primary/30 bg-primary/5 px-4 py-3 shadow-sm">
              <code className="whitespace-nowrap font-mono text-[15px] text-primary">
                npm install -g EvoSec
              </code>
              <CopyButton text="npm install -g EvoSec" />
            </div>
          </div>
        </div>

        {/* Right: Terminal mock with meowBot ASCII */}
        <div className="relative z-10 rounded-2xl border border-border bg-[#1a1b1e] shadow-[0px_10px_30px_rgba(0,0,0,0.15)]">
          {/* Title bar */}
          <div className="flex items-center gap-2 rounded-t-2xl border-b border-white/5 bg-[#2a2c30] px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-red-400"></span>
            <span className="h-3 w-3 rounded-full bg-yellow-400"></span>
            <span className="h-3 w-3 rounded-full bg-green-400"></span>
          </div>

          <pre className="overflow-auto rounded-b-2xl p-6 font-mono text-[13px] leading-6 text-white">
{`
███████╗██╗   ██╗ ██████╗ ███████╗███████╗ ██████╗
██╔════╝██║   ██║██╔═══██╗██╔════╝██╔════╝██╔════╝
█████╗  ██║   ██║██║   ██║███████╗█████╗  ██║     
██╔══╝  ╚██╗ ██╔╝██║   ██║╚════██║██╔══╝  ██║     
███████╗ ╚████╔╝ ╚██████╔╝███████║███████╗╚██████╗
╚══════╝  ╚═══╝   ╚═════╝ ╚══════╝╚══════╝ ╚═════╝



`}
          </pre>
        </div>
      </div>
    </section>
  );
};

export default AnalysisFeatures;