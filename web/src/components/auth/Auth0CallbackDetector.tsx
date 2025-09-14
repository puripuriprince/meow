'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function Auth0CallbackHandler() {
  const { isLoading, error, isAuthenticated, handleRedirectCallback } = useAuth0();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    // If we have auth code parameters, this is a callback
    if (code && state) {
      console.log('Auth0 callback detected with code:', code.substring(0, 10) + '...');
      
      // Auth0 should automatically handle this, but let's give it time
      setTimeout(() => {
        if (!isLoading) {
          if (error) {
            console.error('Auth0 callback error:', error);
            // Clean the URL and show error
            router.replace('/?auth_error=' + encodeURIComponent(error.message));
          } else if (isAuthenticated) {
            console.log('Auth0 callback success - redirecting to dashboard');
            router.replace('/dashboard');
          } else {
            console.log('Auth0 callback completed but not authenticated');
            router.replace('/');
          }
        }
      }, 2000); // Give Auth0 time to process
    }
  }, [searchParams, isLoading, error, isAuthenticated, router]);

  return null; // This component doesn't render anything
}
