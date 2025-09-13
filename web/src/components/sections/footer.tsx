import Image from "next/image";
import Link from "next/link";

const Footer = () => {
  return (
    <footer className="bg-background text-foreground">
      <div className="mx-auto max-w-[1200px] px-6 py-12">
        <div className="flex items-center justify-between">
          {/* removed logo image */}
          <div />
          {/* Empty div for layout structure based on original HTML */}
          <div />
        </div>

        <hr className="my-8 border-border" />

        <div className="flex flex-wrap items-center justify-between gap-y-4">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <p>contact@meowBot.ai</p>
            <p>San Francisco, CA</p>
          </div>
          <p className="text-sm text-muted-foreground">
            © 2025 meowBot.ai. All Rights Reserved
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;