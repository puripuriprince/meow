import Image from "next/image";
import { ArrowRight } from "lucide-react";

export default function FinalCta() {
  return (
    <section
      id="cta"
      className="relative w-full overflow-hidden rounded-[40px] bg-gradient-to-br from-[#6b9fed] to-[#a8c5f0]"
    >
      <Image
        src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/xweeFn1Fr6lYoOrgjbqsKkkeHk-9.png"
        alt="Abstract background pattern"
        width={2249}
        height={1254}
        className="absolute inset-0 h-full w-full object-cover opacity-10"
        priority
      />
      <div className="relative z-10 flex flex-col items-center justify-center gap-10 px-6 py-[120px] text-center">
        <div className="flex flex-col items-center gap-4">
          <h2 className="text-[48px] font-medium leading-[1] text-white">
            From vuln to bounty/PR in minutes
          </h2>
          <p className="max-w-[500px] text-[18px] leading-[1.4] text-white">
            Be among the first teams to automate pentests and turn them into pull requests.
          </p>
        </div>
        {/* Email input + CTA */}
        <div className="w-full max-w-xl">
          <div className="flex items-center rounded-full bg-white p-1 pl-4 shadow-sm border border-[var(--input)] focus-within:ring-2 focus-within:ring-[var(--ring)]">
            <input
              type="email"
              inputMode="email"
              placeholder="Enter email"
              aria-label="Email address"
              className="h-11 w-full flex-1 bg-transparent text-[var(--foreground)] placeholder:text-[var(--muted-foreground)] outline-none"
            />
            <a
              href="https://cal.com/meowBot/20min"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-3 text-[15px] font-medium text-primary shadow-sm transition-colors hover:bg-primary/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-white"
            >
              Get on waitlist
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}