import React from 'react';
import Image from 'next/image';

const PerformanceMonitoring = () => {
  return (
    <section id="services" className="flex flex-col items-center bg-background px-0 pb-20 pt-[120px]">
      <div className="container flex w-full flex-col items-stretch justify-start gap-[60px]">
        <div className="flex flex-col items-center justify-start gap-10 self-center">
          <div className="flex w-full max-w-[600px] flex-col items-center justify-start gap-4 text-center">
            <h2 className="font-display text-[32px] font-semibold leading-[1.3] tracking-[-0.64px] text-text-dark">
              Intelligent Performance Monitoring
            </h2>
            <p className="font-body text-lg leading-[1.6] text-text-gray">
              Real-time performance tracking that instantly tells you what's slow
            </p>
          </div>
          <div className="relative aspect-[1441/803] w-full overflow-hidden rounded-[20px] shadow-[0_2px_4px_0_rgba(0,0,0,0.05),0_8px_16px_0_rgba(0,0,0,0.05),0_16px_32px_0_rgba(0,0,0,0.05)]">
            {/* The HTML structure shows a video, but the screenshot and instructions point to an image. 
                The provided asset is an image, so we use that as per priority. */}
            <Image
              src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/dGJcqUirOtkmZTv9seN80MlTVOY-2.png"
              alt="meowBot.ai performance monitoring dashboard"
              width={1441}
              height={803}
              className="h-full w-full object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
};

export default PerformanceMonitoring;