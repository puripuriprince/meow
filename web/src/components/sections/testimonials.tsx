export default function Testimonials() {
  return (
    <section className="bg-white pt-24 pb-20">
      <div className="container max-w-7xl mx-auto px-6">
        <h2 className="mb-16 text-center text-4xl font-semibold text-[#2c3e50] sm:text-5xl lg:text-6xl">
          What developers say about meowBot
        </h2>
        <div className="grid gap-12 lg:grid-cols-2">
          {/* Testimonial 1 */}
          <div className="group relative">
            <figure className="flex h-full flex-col justify-between rounded-3xl border border-[#e5e8eb] bg-[#f8fafb] p-10 transition-all duration-300 ease-out hover:shadow-lg hover:shadow-black/5 hover:-translate-y-1">
              <div>
                <div className="mb-6 text-6xl font-light leading-none text-[#4a90e2] opacity-60">"</div>
                <blockquote className="mb-8 text-xl leading-relaxed text-[#2c3e50] lg:text-2xl lg:leading-relaxed">
                  meowBot blah blah blah lorem ipsum.
                </blockquote>
              </div>
              <figcaption className="border-t border-[#e5e8eb] pt-6">
                <div className="font-semibold text-[#2c3e50] text-lg">Steve Stevenson</div>
                <div className="text-[#7f8c8d] text-base mt-1">Staff Software Engineer at Revamp</div>
              </figcaption>
            </figure>
          </div>

          {/* Testimonial 2 */}
          <div className="group relative">
            <figure className="flex h-full flex-col justify-between rounded-3xl border border-[#e5e8eb] bg-[#f8fafb] p-10 transition-all duration-300 ease-out hover:shadow-lg hover:shadow-black/5 hover:-translate-y-1">
              <div>
                <div className="mb-6 text-6xl font-light leading-none text-[#4a90e2] opacity-60">"</div>
                <blockquote className="mb-8 text-xl leading-relaxed text-[#2c3e50] lg:text-2xl lg:leading-relaxed">
                  meowBot blah blah blah lorem ipsum.
                </blockquote>
              </div>
              <figcaption className="border-t border-[#e5e8eb] pt-6">
                <div className="font-semibold text-[#2c3e50] text-lg">Marky Mark</div>
                <div className="text-[#7f8c8d] text-base mt-1">VP of AI at Quarcc</div>
              </figcaption>
            </figure>
          </div>
        </div>
      </div>
    </section>
  );
}