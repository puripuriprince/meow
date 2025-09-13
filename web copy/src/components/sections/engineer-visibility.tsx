import React from 'react';
import { ArrowRight } from 'lucide-react';

const EngineerVisibility = () => {
  return (
    <section id="benefits" className="bg-background">
      <div className="container pt-[120px]">
        <div className="mx-auto flex max-w-[610px] flex-col items-center gap-12 text-center">
          <h3 className="font-display text-3xl font-semibold tracking-[-0.02em] text-text-dark">
            meowBot.ai gives your engineers the visibility they've been missing.
          </h3>
          <a
            href="https://cal.com/herdora/20min"
            target="_blank"
            rel="noopener noreferrer"
            className="group flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-primary transition-colors hover:text-primary/80"
          >
            <span>Get on the waitlist</span>
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </a>
        </div>
      </div>
      <div className="container">
        <div className="h-px w-full bg-gradient-to-r from-transparent via-border to-transparent" />
      </div>
    </section>
  );
};

export default EngineerVisibility;