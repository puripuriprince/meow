import Image from "next/image";
import { KeyRound, ArrowRight, Image as ImageIcon } from "lucide-react";

const cards = [
  {
    imageUrl: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/iEjxcAIayejRQXHEXpzJMipN2M-6.png",
    title: "Root Cause Analysis",
    description: "Pinpoint whether the bottleneck is model code, data loading, memory I/O, or a specific GPU/PCIe limitation. Get a definitive answer—not guesses.",
  },
  {
    imageUrl: null,
    title: "Production-Scenario Simulation",
    description: "Profile realistically scaled workloads before they hit prod to catch issues early.",
  },
  {
    imageUrl: null,
    title: "Layer-by-Layer Visualization",
    description: "See a visual map of your model and the exact operators/kernels costing you performance.",
  },
];

export default function GpuProfiling() {
  return (
    <section id="services-1" className="bg-background py-20 lg:py-24">
      <div className="container max-w-7xl mx-auto px-6">
        <div className="flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50/50 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-primary-blue">
            <KeyRound className="h-3.5 w-3.5" />
            <span>KEYS &amp; CACHES</span>
          </div>

          <h2 className="mt-6 text-3xl font-semibold text-text-dark md:text-4xl leading-tight">
            Automated GPU Profiling
          </h2>

          <p className="mt-4 max-w-2xl text-lg text-text-gray">
            Identify the root cause of slowdowns in seconds.
          </p>

          <a
            href="https://www.keysandcaches.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 text-base font-medium text-primary-blue transition-colors hover:text-blue-700"
          >
            TRY OUR SDK
            <ArrowRight className="h-4 w-4" />
          </a>
        </div>

        <div className="mt-16 w-full max-w-6xl mx-auto">
          <div className="relative w-full h-[250px] overflow-hidden rounded-lg bg-gradient-to-br from-blue-100/30 to-indigo-100/30 p-6 shadow-inner">
            <div className="space-y-3">
              <div style={{ width: '100%' }} className="h-10 rounded bg-gradient-to-r from-blue-300 to-blue-200 opacity-60"></div>
              <div style={{ width: '85%', marginLeft: '5%' }} className="h-6 rounded bg-gradient-to-r from-blue-300 to-blue-200 opacity-50"></div>
              <div style={{ width: '95%' }} className="h-4 rounded bg-gradient-to-r from-blue-300 to-blue-200 opacity-60"></div>
              <div className="pt-4 flex items-end justify-between gap-2">
                <div style={{ height: '70px', width: '15%' }} className="rounded bg-gradient-to-b from-blue-300 to-blue-400 opacity-70"></div>
                <div style={{ height: '40px', width: '20%' }} className="rounded bg-gradient-to-b from-blue-200 to-blue-300 opacity-70"></div>
                <div style={{ height: '60px', width: '10%' }} className="rounded bg-gradient-to-b from-blue-300 to-blue-400 opacity-70"></div>
                <div style={{ height: '80px', width: '30%' }} className="rounded bg-gradient-to-b from-blue-200 to-blue-400 opacity-70"></div>
                <div style={{ height: '50px', width: '15%' }} className="rounded bg-gradient-to-b from-blue-200 to-blue-300 opacity-70"></div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {cards.map((card) => (
            <div key={card.title} className="bg-white border border-border-light rounded-2xl p-8 flex flex-col items-start text-left h-full transition-shadow duration-300 hover:shadow-xl">
              <div className="w-full h-40 mb-6 flex items-center justify-center rounded-lg bg-secondary">
                {card.imageUrl ? (
                  <Image
                    src={card.imageUrl}
                    alt={card.title}
                    width={150}
                    height={150}
                    className="object-contain h-full w-auto"
                  />
                ) : (
                  <ImageIcon className="w-12 h-12 text-muted-foreground" />
                )}
              </div>
              <h3 className="text-xl font-semibold text-text-dark">
                {card.title}
              </h3>
              <p className="mt-2 text-base text-text-gray flex-grow">
                {card.description}
              </p>
            </div>
          ))}
        </div>
      </div>
      <div className="container max-w-7xl mx-auto px-6 mt-24">
        <div className="border-t border-border-light"></div>
      </div>
    </section>
  );
}