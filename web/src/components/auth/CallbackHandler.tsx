'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function CallbackHandler() {
  const { isLoading, isAuthenticated, error } = useAuth0();
  const router = useRouter();

  useEffect(() => {
    // If authentication is complete and successful, redirect to dashboard
    if (!isLoading && isAuthenticated) {
      console.log('Auth successful, redirecting to dashboard');
      router.push('/dashboard');
    }

    // If there's an error, log it
    if (error) {
      console.error('Auth callback error:', error);
    }
  }, [isLoading, isAuthenticated, error, router]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Processing authentication...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Authentication failed</p>
          <p className="text-gray-600">{error.message}</p>
        </div>
      </div>
    );
  }

  return null;
}
