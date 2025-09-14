import React from 'react'
import Navigation from "@/components/sections/navigation"
import Footer from "@/components/sections/footer"

export default function ComingSoonPage() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />
      <section className="container max-w-4xl mx-auto px-6 pt-40 pb-24">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-semibold text-foreground">Coming soon</h1>
          <p className="text-body-large mt-2">We're building this page. Check back shortly.</p>
        </div>
        <div className="relative z-10 rounded-2xl border border-border bg-[#1a1b1e] shadow-[0px_10px_30px_rgba(0,0,0,0.15)]">
          <div className="flex items-center gap-2 rounded-t-2xl border-b border-white/5 bg-[#2a2c30] px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-red-400"></span>
            <span className="h-3 w-3 rounded-full bg-yellow-400"></span>
            <span className="h-3 w-3 rounded-full bg-green-400"></span>
          </div>
          <pre className="overflow-auto rounded-b-2xl p-6 font-mono text-[13px] leading-6 text-white">
{`meowBot@terminal:~$ echo "When launch?"
COMING SOON

# We're cooking something great.
# Check back soon.
`}
          </pre>
        </div>
      </section>
      <Footer />
    </main>
  )
}