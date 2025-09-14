import Image from "next/image";

const HeroSection = () => {
  return (
    <section
      id="hero"
      className="relative flex flex-col items-center overflow-hidden bg-white pt-2 pb-20 text-center"
    >
      <div className="container max-w-none">
        <div className="flex flex-col items-center gap-8">
          {/* Rectangular image with centered overlay text */}
          <div className="relative w-full h-[80vh] md:h-[90vh] overflow-hidden rounded-2xl md:rounded-3xl">
            <Image
              src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/xweeFn1Fr6lYoOrgjbqsKkkeHk-9.png"
              alt="Abstract background"
              fill
              className="object-cover"
              priority
            />
            <div className="absolute inset-0 flex flex-col items-center justify-center px-6">
              <h1 className="text-3xl md:text-5xl font-semibold leading-tight tracking-tighter text-primary">
                EvoSec, the hacking agent in your terminal.
              </h1>
              <p className="mt-3 text-base md:text-lg text-primary/80">
                Penetration testing at terminal velocity.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;