import React from "react";

const logos: { name: string; className?: string }[] = [
  { name: "Jump Trading" },
  { name: "Revamp", className: "text-[#4a90e2] font-semibold" },
  { name: "Meta" },
  { name: "JaneStreet" },
  { name: "Mosaic" },
  { name: "Amazon" },
];

function LogoRow() {
  return (
    <div className="flex items-center gap-8 sm:gap-12 md:gap-16 lg:gap-20 pr-8 sm:pr-12 md:pr-16 lg:pr-20">
      {logos.map((logo, idx) => (
        <span
          key={`${logo.name}-${idx}`}
          className={`text-lg sm:text-xl md:text-2xl font-medium tracking-tight text-foreground/70 whitespace-nowrap ${logo.className || ""}`}
        >
          {logo.name}
        </span>
      ))}
    </div>
  );
}

export default function TrustedBy() {
  return (
    <section className="relative bg-background py-12 md:py-16 lg:py-20 overflow-hidden">
      {/* background overlay removed to match other sections */}

      <div className="container max-w-7xl mx-auto px-6 relative">
        <h3 className="text-center text-lg md:text-xl lg:text-2xl font-medium text-foreground/80 mb-8 md:mb-12 lg:mb-16">
          Trusted by engineers at
        </h3>
      </div>

      <div
        className="relative w-screen left-1/2 right-1/2 -ml-[50vw] -mr-[50vw] overflow-hidden"
        aria-label="Scrolling logos of trusted companies"
        role="region"
      >
        {/* Primary track */}
        <div className="flex w-max animate-[trusted-marquee_40s_linear_infinite] will-change-transform">
          <LogoRow />
          <LogoRow />
          <LogoRow />
          <LogoRow />
        </div>

        {/* Secondary track for seamless loop */}
        <div className="absolute top-0 left-0 hidden sm:flex w-max animate-[trusted-marquee_40s_linear_infinite] [animation-delay:-20s] will-change-transform" aria-hidden="true">
          <LogoRow />
          <LogoRow />
          <LogoRow />
          <LogoRow />
        </div>
      </div>
    </section>
  );
}