'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Auth0CallbackHandler() {
  const { isLoading, error, isAuthenticated } = useAuth0();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (error) {
        console.error('Auth0 Callback Error:', error);
        // Redirect to home with error
        router.push('/?auth_error=' + encodeURIComponent(error.message));
      } else if (isAuthenticated) {
        console.log('Auth0 Callback Success - redirecting to dashboard');
        router.push('/dashboard');
      }
    }
  }, [isLoading, error, isAuthenticated, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Authentication Error</h1>
          <p className="text-gray-600 mb-4">{error.message}</p>
          <button 
            onClick={() => router.push('/')}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            Return Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p>Completing authentication...</p>
      </div>
    </div>
  );
}
