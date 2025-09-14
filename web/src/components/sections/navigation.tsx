'use client';

import Link from 'next/link';
import AuthButton from '@/components/auth/AuthButton';
import WalletButton from '@/components/solana/WalletButton';

export default function Navigation() {
  return (
    <div className="fixed top-2.5 left-1/2 -translate-x-1/2 z-50">
      <header className="flex items-center gap-x-6 rounded-full bg-white/50 py-2.5 pl-5 pr-4 shadow-[0_0_10px_3px_rgba(219,219,219,0.25)] backdrop-blur-md">
        <Link href="/" className="flex-shrink-0">
          <span className="font-display text-lg font-semibold text-text-dark whitespace-nowrap">
            EvoSec
          </span>
        </Link>
        
        {/* Auth and Wallet Section */}
        <div className="flex items-center gap-3 ml-4">
          <WalletButton />
          <AuthButton />
        </div>
      </header>
    </div>
  );
}