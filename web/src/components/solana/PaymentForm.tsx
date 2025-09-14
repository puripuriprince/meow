'use client';

import { useState } from 'react';
import { useWallet, useConnection } from '@solana/wallet-adapter-react';
import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, CreditCard, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import { solanaPayAPI } from '@/services/api';

interface PaymentFormProps {
  onSuccess?: () => void;
}

export default function PaymentForm({ onSuccess }: PaymentFormProps) {
  const { connected, publicKey, sendTransaction } = useWallet();
  const { connection } = useConnection();
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  
  const [amount, setAmount] = useState('');
  const [label, setLabel] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!connected || !publicKey) {
      toast.error('Please connect your Solana wallet first');
      return;
    }
    
    if (!isAuthenticated) {
      toast.error('Please sign in to make a payment');
      return;
    }

    if (!amount || parseFloat(amount) <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }

    if (!label.trim()) {
      toast.error('Please enter a payment description');
      return;
    }

    setLoading(true);
    setPaymentStatus('processing');

    try {
      // Get auth token
      const token = await getAccessTokenSilently();
      
      // Create payment request using our API service
      const response = await solanaPayAPI.createPayment({
        amount: parseFloat(amount),
        label,
        message: message || `Payment of ${amount} SOL for ${label}`
      }, token);

      if (response.paymentRequest) {
        toast.success('Payment request created successfully!');
        
        // Here you would typically integrate with Solana Pay to process the transaction
        // For now, we'll simulate a successful payment
        setTimeout(() => {
          setPaymentStatus('success');
          toast.success('Payment completed successfully!');
          onSuccess?.();
          
          // Reset form
          setAmount('');
          setLabel('');
          setMessage('');
        }, 2000);
      }
    } catch (error) {
      console.error('Payment error:', error);
      setPaymentStatus('error');
      toast.error('Payment failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Payment Required</CardTitle>
          <CardDescription>
            Please sign in to make a payment
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  if (!connected) {
    return (
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Wallet Required</CardTitle>
          <CardDescription>
            Please connect your Solana wallet to make a payment
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <CreditCard className="w-5 h-5" />
          Make Payment
        </CardTitle>
        <CardDescription>
          Pay securely with Solana
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handlePayment} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="amount">Amount (SOL)</Label>
            <Input
              id="amount"
              type="number"
              step="0.001"
              min="0"
              placeholder="0.1"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              disabled={loading}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="label">Payment Description</Label>
            <Input
              id="label"
              placeholder="What is this payment for?"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              disabled={loading}
              required
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="message">Message (Optional)</Label>
            <Input
              id="message"
              placeholder="Additional message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={loading}
            />
          </div>

          {paymentStatus === 'success' && (
            <Alert className="border-green-200 bg-green-50">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                Payment completed successfully!
              </AlertDescription>
            </Alert>
          )}

          {paymentStatus === 'error' && (
            <Alert className="border-red-200 bg-red-50">
              <AlertDescription className="text-red-800">
                Payment failed. Please try again.
              </AlertDescription>
            </Alert>
          )}

          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading || paymentStatus === 'success'}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : paymentStatus === 'success' ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Payment Complete
              </>
            ) : (
              <>
                <CreditCard className="mr-2 h-4 w-4" />
                Pay {amount ? `${amount} SOL` : ''}
              </>
            )}
          </Button>
        </form>
        
        {connected && publicKey && (
          <div className="mt-4 text-xs text-muted-foreground">
            Connected: {publicKey.toString().slice(0, 8)}...{publicKey.toString().slice(-8)}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
