'use client';

import { ReactNode } from 'react';
import Auth0ProviderWrapper from './Auth0Provider';
import SolanaWalletProvider from './SolanaWalletProvider';

interface ProvidersProps {
  children: ReactNode;
}

export default function Providers({ children }: ProvidersProps) {
  return (
    <Auth0ProviderWrapper>
      <SolanaWalletProvider>
        {children}
      </SolanaWalletProvider>
    </Auth0ProviderWrapper>
  );
}
