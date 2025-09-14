'use client';

import { useState, useEffect } from 'react';

export interface SolanaPriceData {
  usdPrice: number;
  solAmount: number;
  isLoading: boolean;
  error: string | null;
}

export function useSolanaPrice(usdAmount: number): SolanaPriceData {
  const [priceData, setPriceData] = useState<SolanaPriceData>({
    usdPrice: 0,
    solAmount: 0,
    isLoading: true,
    error: null
  });

  useEffect(() => {
    const fetchSolanaPrice = async () => {
      try {
        setPriceData(prev => ({ ...prev, isLoading: true, error: null }));
        
        const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd');
        
        if (!response.ok) {
          throw new Error('Failed to fetch Solana price');
        }
        
        const data = await response.json();
        const solPrice = data.solana?.usd;
        
        if (!solPrice) {
          throw new Error('Invalid price data received');
        }
        
        const solAmount = usdAmount / solPrice;
        
        setPriceData({
          usdPrice: solPrice,
          solAmount: Math.round(solAmount * 1000000) / 1000000, // Round to 6 decimal places
          isLoading: false,
          error: null
        });
      } catch (error) {
        console.error('Error fetching Solana price:', error);
        setPriceData(prev => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }));
      }
    };

    fetchSolanaPrice();
    
    // Update price every 30 seconds
    const interval = setInterval(fetchSolanaPrice, 30000);
    
    return () => clearInterval(interval);
  }, [usdAmount]);

  return priceData;
}
