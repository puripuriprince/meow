'use client';

import { Auth0Provider } from '@auth0/auth0-react';
import { ReactNode } from 'react';

interface Auth0ProviderWrapperProps {
  children: ReactNode;
}

export default function Auth0ProviderWrapper({ children }: Auth0ProviderWrapperProps) {
  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN!;
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!;
  
  console.log('Auth0 Provider Init:', { 
    domain: domain ? 'SET' : 'MISSING', 
    clientId: clientId ? 'SET' : 'MISSING',
    redirectUri: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8080'
  });
  
  if (!domain || !clientId) {
    console.error('Missing Auth0 configuration');
    return <>{children}</>;
  }

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8080',
        scope: "openid profile email"
      }}
      skipRedirectCallback={false}
      cacheLocation="localstorage"
      useRefreshTokens={false}
    >
      {children}
    </Auth0Provider>
  );
}
