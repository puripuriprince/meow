import type { Metadata } from "next";
import "./globals.css";
import VisualEditsMessenger from "../visual-edits/VisualEditsMessenger";
import ErrorReporter from "@/components/ErrorReporter";
import Script from "next/script";
import Providers from "@/contexts/Providers";

export const metadata: Metadata = {
  title: "EvoSec - Agentic Cybersecurity",
  description: "Advanced web3 security and payment solutions for the modern digital economy",
  keywords: ["cybersecurity", "web3", "solana", "security", "agentic", "AI", "blockchain"],
  authors: [{ name: "EvoSec" }],
  creator: "EvoSec",
  publisher: "EvoSec",
  icons: {
    icon: "/EvoSec.png",
    shortcut: "/EvoSec.png",
    apple: "/EvoSec.png",
  },
  openGraph: {
    title: "EvoSec - Agentic Cybersecurity",
    description: "Advanced web3 security and payment solutions for the modern digital economy",
    url: "https://evosec.ai",
    siteName: "EvoSec",
    images: [
      {
        url: "/EvoSec.png",
        width: 800,
        height: 600,
        alt: "EvoSec Logo",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "EvoSec - Agentic Cybersecurity",
    description: "Advanced web3 security and payment solutions for the modern digital economy",
    images: ["/EvoSec.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          <ErrorReporter />
          <Script
            src="https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/object/public/scripts//route-messenger.js"
            strategy="afterInteractive"
            data-target-origin="*"
            data-message-type="ROUTE_CHANGE"
            data-include-search-params="true"
            data-only-in-iframe="true"
            data-debug="true"
            data-custom-data='{"appName": "YourApp", "version": "1.0.0", "greeting": "hi"}'
          />
          {children}
          <VisualEditsMessenger />
        </Providers>
      </body>
    </html>
  );
}
