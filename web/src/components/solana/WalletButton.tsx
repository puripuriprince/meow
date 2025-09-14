'use client';

import { useWallet } from '@solana/wallet-adapter-react';
import { useWalletModal } from '@solana/wallet-adapter-react-ui';
import { Button } from '@/components/ui/button';
import { Wallet } from 'lucide-react';
import { useState } from 'react';

export default function WalletButton() {
  const { connected, publicKey, disconnect } = useWallet();
  const { setVisible } = useWalletModal();
  const [showDetails, setShowDetails] = useState(false);

  const handleClick = () => {
    if (connected) {
      setShowDetails(!showDetails);
    } else {
      setVisible(true);
    }
  };

  const handleDisconnect = () => {
    disconnect();
    setShowDetails(false);
  };

  if (connected && publicKey) {
    return (
      <div className="relative">
        <Button
          onClick={handleClick}
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 text-sm font-medium rounded-lg flex items-center gap-2"
        >
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          Connected
        </Button>
        
        {showDetails && (
          <div className="absolute top-full mt-2 right-0 bg-white border border-gray-200 rounded-lg shadow-lg p-4 min-w-[250px] z-50">
            <div className="space-y-3">
              <div>
                <p className="text-sm font-medium text-gray-700">Wallet Address:</p>
                <p className="text-xs text-gray-600 font-mono break-all">
                  {publicKey.toString()}
                </p>
              </div>
              <div className="pt-2 border-t border-gray-200">
                <Button
                  onClick={handleDisconnect}
                  variant="outline"
                  size="sm"
                  className="w-full text-red-600 border-red-200 hover:bg-red-50"
                >
                  Disconnect
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <Button
      onClick={handleClick}
      className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 text-sm font-medium rounded-lg flex items-center gap-2"
    >
      <Wallet className="w-4 h-4" />
      Connect Wallet
    </Button>
  );
}
