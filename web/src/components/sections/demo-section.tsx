'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Shield, Wallet, CreditCard, Zap, ArrowRight, CheckCircle } from 'lucide-react';
import Link from 'next/link';
import { useAuth0 } from '@auth0/auth0-react';
import { useWallet } from '@solana/wallet-adapter-react';

export default function DemoSection() {
  const { isAuthenticated } = useAuth0();
  const { connected } = useWallet();

  const features = [
    {
      icon: Shield,
      title: "Auth0 Authentication",
      description: "Secure login with industry-standard authentication",
      status: isAuthenticated ? "connected" : "disconnected",
      action: isAuthenticated ? "Authenticated ✓" : "Sign In"
    },
    {
      icon: Wallet,
      title: "Solana Wallet",
      description: "Connect your Phantom, Solflare, or other Solana wallets",
      status: connected ? "connected" : "disconnected",
      action: connected ? "Connected ✓" : "Connect Wallet"
    },
    {
      icon: CreditCard,
      title: "Solana Pay",
      description: "Fast, secure payments on the Solana blockchain",
      status: isAuthenticated && connected ? "ready" : "pending",
      action: isAuthenticated && connected ? "Ready to Pay" : "Setup Required"
    }
  ];

  return (
    <section className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="container max-w-7xl mx-auto px-6">
        <div className="text-center mb-16">
          <Badge variant="outline" className="mb-4">
            <Zap className="w-4 h-4 mr-2" />
            Secure Payments
          </Badge>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Web3 Payment Integration
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Secure authentication and payment flow with Auth0 and Solana Pay integration
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="relative overflow-hidden">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${
                        feature.status === 'connected' || feature.status === 'ready' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{feature.title}</CardTitle>
                      </div>
                    </div>
                    <Badge 
                      variant={
                        feature.status === 'connected' || feature.status === 'ready' 
                          ? 'default' 
                          : 'secondary'
                      }
                      className={
                        feature.status === 'connected' || feature.status === 'ready'
                          ? 'bg-green-100 text-green-700 border-green-200'
                          : ''
                      }
                    >
                      {feature.status === 'connected' || feature.status === 'ready' ? (
                        <CheckCircle className="w-3 h-3 mr-1" />
                      ) : null}
                      {feature.action}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            );
          })}
        </div>

        <div className="text-center">
          <Card className="inline-block p-8 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-dashed border-blue-200">
            <div className="flex flex-col items-center gap-4">
              <div className="text-2xl font-bold text-gray-900">
                {isAuthenticated && connected ? '🎉 All Set!' : '👆 Get Started'}
              </div>
              <p className="text-gray-600 max-w-md">
                {isAuthenticated && connected 
                  ? 'You\'re ready to make secure payments with Solana Pay!'
                  : 'Connect your wallet and sign in to experience the full payment flow'}
              </p>
              <Link href="/dashboard">
                <Button size="lg" className="mt-2">
                  {isAuthenticated && connected ? 'Go to Dashboard' : 'Try Demo'}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </div>
    </section>
  );
}
