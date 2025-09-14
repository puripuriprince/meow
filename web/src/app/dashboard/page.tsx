'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { useWallet } from '@solana/wallet-adapter-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Wallet, CreditCard, User, Shield } from 'lucide-react';
import { useSolanaPrice } from '@/hooks/useSolanaPrice';
import WalletButton from '@/components/solana/WalletButton';
import AuthButton from '@/components/auth/AuthButton';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth0();
  const { connected, publicKey } = useWallet();
  const proPriceData = useSolanaPrice(150); // $150 USD for Pro plan

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-6 p-6">
          <Card>
            <CardHeader className="text-center">
              <Shield className="h-12 w-12 mx-auto text-blue-600 mb-4" />
              <CardTitle>Access Required</CardTitle>
              <CardDescription>
                Please sign in to access your dashboard
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <AuthButton />
              <div className="text-center">
                <Link href="/" className="text-sm text-blue-600 hover:underline">
                  ← Back to Home
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-4">
              <Link href="/" className="font-display text-xl font-semibold text-gray-900">
                EvoSec
              </Link>
              <span className="text-gray-400">|</span>
              <h1 className="text-2xl font-bold text-gray-900">
                Dashboard
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <WalletButton />
              <AuthButton />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* User Info */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Profile
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  {user?.picture && (
                    <img 
                      src={user.picture} 
                      alt={user.name || 'User'} 
                      className="h-12 w-12 rounded-full"
                    />
                  )}
                  <div>
                    <p className="font-medium">{user?.name}</p>
                    <p className="text-sm text-gray-500">{user?.email}</p>
                  </div>
                </div>
                
                {user?.email_verified && (
                  <div className="flex items-center gap-2 text-green-600">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm">Email Verified</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Wallet Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wallet className="h-5 w-5" />
                  Wallet Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {connected && publicKey ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-green-600">
                      <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm font-medium">Connected</span>
                    </div>
                    <p className="text-xs text-gray-500 font-mono">
                      {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-gray-500">
                      <div className="h-2 w-2 bg-gray-400 rounded-full"></div>
                      <span className="text-sm">Not Connected</span>
                    </div>
                    <WalletButton />
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Payment Section */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Subscription Plans
                </CardTitle>
                <CardDescription>
                  Choose your EvoSec plan and subscribe using Solana blockchain payments
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Subscription Plans */}
                  <div className="grid gap-4">
                    {/* Pro Plan */}
                    <div className="border rounded-lg p-6 bg-blue-50 border-blue-200">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-blue-900">EvoSec Pro</h3>
                          <p className="text-sm text-blue-700 mt-1">Advanced cybersecurity features and unlimited scans</p>
                        </div>
                        <div className="text-right">
                          <div className="text-3xl font-bold text-blue-900">$150</div>
                          <div className="text-sm text-blue-600">per month</div>
                        </div>
                      </div>
                      
                      {/* Real-time SOL conversion */}
                      <div className="bg-white rounded-lg p-4 border border-blue-200">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-gray-700">Equivalent in SOL:</span>
                          {proPriceData.isLoading ? (
                            <div className="flex items-center gap-2">
                              <Loader2 className="h-4 w-4 animate-spin" />
                              <span className="text-sm text-gray-500">Loading...</span>
                            </div>
                          ) : proPriceData.error ? (
                            <span className="text-sm text-red-500">Price unavailable</span>
                          ) : (
                            <div className="text-right">
                              <div className="font-bold text-lg text-blue-900">{proPriceData.solAmount.toFixed(4)} SOL</div>
                              <div className="text-xs text-gray-500">≈ ${proPriceData.usdPrice.toFixed(2)}/SOL</div>
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <Button className="w-full mt-4 bg-blue-600 hover:bg-blue-700" disabled={!connected || proPriceData.isLoading}>
                        {connected ? 'Subscribe to Pro' : 'Connect Wallet to Subscribe'}
                      </Button>
                    </div>

                    {/* Enterprise Plan */}
                    <div className="border rounded-lg p-6 bg-gray-50 border-gray-200">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">EvoSec Enterprise</h3>
                          <p className="text-sm text-gray-700 mt-1">Custom solutions, dedicated support, and enterprise-grade security</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-900">Contact Us</div>
                          <div className="text-sm text-gray-600">Custom pricing</div>
                        </div>
                      </div>
                      
                      <Button variant="outline" className="w-full mt-4">
                        Get Enterprise Quote
                      </Button>
                    </div>
                  </div>
                  
                  {/* Automatic Payment Info */}
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <Shield className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
                      <div className="text-sm text-amber-800">
                        <p className="font-medium mb-1">Automatic Monthly Billing</p>
                        <p>
                          When you subscribe to any EvoSec plan, the subscription amount will be automatically 
                          deducted from your connected Solana wallet each month on your billing date. You can 
                          cancel your subscription at any time from your account settings. All transactions 
                          are secured by the Solana blockchain for maximum transparency and security.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Subscription Status */}
            <Card>
              <CardHeader>
                <CardTitle>Subscription Status</CardTitle>
                <CardDescription>
                  Manage your EvoSec Pro subscription
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert>
                  <AlertDescription>
                    No active subscription. Connect your wallet and subscribe to get started with EvoSec Pro features!
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
