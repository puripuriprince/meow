import Navigation from '@/components/sections/navigation';
import HeroSection from '@/components/sections/hero';
import AnalysisFeatures from '@/components/sections/analysis-features';
import FinalCta from '@/components/sections/final-cta';
import Footer from '@/components/sections/footer';
import TrustedBy from '@/components/sections/trusted-by';
import Examples from '@/components/sections/examples';
import Testimonials from '@/components/sections/testimonials';
import FAQSection from '@/components/sections/faq';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white">
      <Navigation />
      
      <div className="flex flex-col">
        <HeroSection />
        
        <div className="bg-background">
          <div className="container max-w-7xl mx-auto px-6">
            <AnalysisFeatures />
          </div>
        </div>
        
        <TrustedBy />
        
        {/* Full-viewport horizontally scrollable examples */}
        <Examples />
        {/* <Testimonials /> */}
        {/* FAQ section */}
        <FAQSection />
        
        <div className="bg-background pt-20 pb-0">
          <div className="container max-w-7xl mx-auto px-6">
            <FinalCta />
          </div>
        </div>
        
        <Footer />
      </div>
    </main>
  );
}