import Image from "next/image";

const features = [
  {
    icon: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/fqJLgLK5peWoAw1MArXXMztTEww-3.png",
    title: "Continuous Optimization",
    description: "Our system learns from your production traffic, implementing new opportunities for optimization automatically.",
  },
  {
    icon: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/C6lLFTsLEsWtWSU2DZ8oOXKc-4.png",
    title: "Alerts with Answers",
    description: "Get notified not just that performance degraded, but exactly which commit or change caused the issue.",
  },
  {
    icon: "https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/test-clones/de1bfc8f-a26f-486a-9869-b75e79698d61-herdora-com/assets/images/5cjCAN9nr02vqqtmNoV8bFjetA-5.png",
    title: "Maintain Peak Performance",
    description: "Ensure your models stay fast over time and deploy new versions with confidence.",
  },
];

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => (
  <div className="bg-background border border-border rounded-xl p-8 shadow-[0_2px_8px_rgba(0,0,0,0.08)] hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] transition-shadow duration-200 flex flex-col items-start text-left">
    <div className="mb-6">
      <div className="bg-primary/10 inline-block p-3 rounded-lg">
        <Image src={icon} alt={`${title} icon`} width={40} height={40} className="object-contain" />
      </div>
    </div>
    <div className="flex flex-col">
      <h4 className="text-xl font-semibold text-text-dark">{title}</h4>
      <p className="text-base text-text-gray mt-2 leading-[1.5]">
        {description}
      </p>
    </div>
  </div>
);

const FeaturesGrid = () => {
  return (
    <section id="services" className="bg-background w-full py-20 lg:py-24">
      <div className="container max-w-6xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h3 className="text-3xl font-semibold text-text-dark tracking-tight">
            Intelligent Performance Monitoring
          </h3>
          <p className="text-lg text-text-gray mt-4 max-w-xl mx-auto">
            Real-time performance tracking that instantly tells you what's slow
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesGrid;