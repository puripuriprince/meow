"use client";

import * as React from "react";
import { Clipboard, ClipboardCheck } from "lucide-react";

export type CopyButtonProps = {
  text: string;
  className?: string;
};

export const CopyButton: React.FC<CopyButtonProps> = ({ text, className }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = React.useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch (e) {
      // silently fail
    }
  }, [text]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      aria-label="Copy to clipboard"
      className={`ml-2 inline-flex h-6 w-6 items-center justify-center rounded-md transition-all duration-200 ease-out hover:bg-primary/10 hover:scale-105 active:scale-95 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 ${className ?? ""}`}
    >
      {copied ? (
        <ClipboardCheck className="h-4 w-4 text-primary animate-in fade-in-0 scale-in-95 duration-200" />
      ) : (
        <Clipboard className="h-4 w-4 text-primary transition-opacity duration-200 hover:opacity-80" />
      )}
    </button>
  );
};