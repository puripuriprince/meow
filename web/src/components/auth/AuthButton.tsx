'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import { LogIn, LogOut, User, LayoutDashboard } from 'lucide-react';
import Link from 'next/link';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function AuthButton() {
  const { user, isAuthenticated, isLoading, loginWithRedirect, logout, error } = useAuth0();

  console.log('Auth0 Debug:', { 
    isAuthenticated, 
    isLoading, 
    hasUser: !!user, 
    error: error?.message || 'No error',
    fullError: error 
  });

  if (error) {
    console.error('Auth0 Full Error:', error);
    return (
      <div className="flex flex-col gap-2">
        <Button 
          variant="destructive" 
          onClick={() => {
            localStorage.clear();
            sessionStorage.clear();
            window.location.href = '/';
          }}
        >
          Auth Error: {error.message} - Reset
        </Button>
        <details className="text-xs text-gray-600">
          <summary>Error Details</summary>
          <pre className="mt-2 text-xs bg-gray-100 p-2 rounded">
            {JSON.stringify(error, null, 2)}
          </pre>
        </details>
      </div>
    );
  }

  if (isLoading) {
    return (
      <Button variant="outline" disabled>
        Loading...
      </Button>
    );
  }

  if (isAuthenticated && user) {
    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" className="h-10 px-3 rounded-full">
            <Avatar className="h-7 w-7 mr-2">
              <AvatarImage src={user.picture} alt={user.name || 'User'} />
              <AvatarFallback>
                {user.name?.charAt(0).toUpperCase() || 'U'}
              </AvatarFallback>
            </Avatar>
            <span className="hidden sm:block">
              {user.name?.split(' ')[0] || 'User'}
            </span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end">
          <DropdownMenuLabel>
            <div>
              <p className="text-sm font-medium">{user.name || 'User'}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/dashboard">
              <LayoutDashboard className="mr-2 h-4 w-4" />
              Dashboard
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
  }

  return (
    <Button onClick={() => loginWithRedirect()}>
      <LogIn className="mr-2 h-4 w-4" />
      Sign In
    </Button>
  );
}
