import { Connection, PublicKey, LAMPORTS_PER_SOL } from '@solana/web3.js';
import { createTransferCheckedInstruction, getAssociatedTokenAddress, createAssociatedTokenAccountInstruction } from '@solana/spl-token';
import BigNumber from 'bignumber.js';

export class SolanaPayService {
  private connection: Connection;
  private merchantWallet: PublicKey;

  constructor() {
    const rpcUrl = process.env.SOLANA_RPC_URL || 'https://api.devnet.solana.com';
    const merchantWalletAddress = process.env.MERCHANT_WALLET;

    if (!merchantWalletAddress) {
      throw new Error('Merchant wallet address is not configured');
    }

    this.connection = new Connection(rpcUrl, 'confirmed');
    this.merchantWallet = new PublicKey(merchantWalletAddress);
  }

  async createPaymentRequest(amount: number, label: string, message?: string) {
    try {
      const amountInLamports = new BigNumber(amount).multipliedBy(LAMPORTS_PER_SOL);

      const paymentRequest = {
        recipient: this.merchantWallet.toString(),
        amount: amountInLamports.toString(),
        splToken: null, // null for SOL payments
        reference: this.generateReference(),
        label,
        message: message || `Payment of ${amount} SOL`,
        memo: `Payment for ${label}`,
      };

      return {
        success: true,
        paymentRequest,
        paymentUrl: this.createPaymentUrl(paymentRequest)
      };
    } catch (error) {
      console.error('Error creating payment request:', error);
      return {
        success: false,
        error: 'Failed to create payment request'
      };
    }
  }

  async createTokenPaymentRequest(
    tokenMint: string,
    amount: number,
    decimals: number,
    label: string,
    message?: string
  ) {
    try {
      const tokenMintPubkey = new PublicKey(tokenMint);
      const amountInTokenUnits = new BigNumber(amount).multipliedBy(Math.pow(10, decimals));

      const paymentRequest = {
        recipient: this.merchantWallet.toString(),
        amount: amountInTokenUnits.toString(),
        splToken: tokenMint,
        reference: this.generateReference(),
        label,
        message: message || `Payment of ${amount} tokens`,
        memo: `Token payment for ${label}`,
      };

      return {
        success: true,
        paymentRequest,
        paymentUrl: this.createPaymentUrl(paymentRequest)
      };
    } catch (error) {
      console.error('Error creating token payment request:', error);
      return {
        success: false,
        error: 'Failed to create token payment request'
      };
    }
  }

  async verifyPayment(signature: string, expectedAmount: number, reference?: string) {
    try {
      const transaction = await this.connection.getTransaction(signature, {
        commitment: 'confirmed'
      });

      if (!transaction) {
        return {
          success: false,
          error: 'Transaction not found'
        };
      }

      // Verify the transaction was successful
      if (transaction.meta?.err) {
        return {
          success: false,
          error: 'Transaction failed'
        };
      }

      // Basic verification - you may want to add more checks
      const isValid = this.validateTransaction(transaction, expectedAmount, reference);

      return {
        success: isValid,
        transaction,
        verified: isValid
      };
    } catch (error) {
      console.error('Error verifying payment:', error);
      return {
        success: false,
        error: 'Failed to verify payment'
      };
    }
  }

  async getTransactionStatus(signature: string) {
    try {
      const status = await this.connection.getSignatureStatus(signature);
      
      return {
        success: true,
        status: status.value,
        confirmed: status.value?.confirmationStatus === 'confirmed' || 
                  status.value?.confirmationStatus === 'finalized'
      };
    } catch (error) {
      console.error('Error getting transaction status:', error);
      return {
        success: false,
        error: 'Failed to get transaction status'
      };
    }
  }

  private generateReference(): string {
    // Generate a unique reference for the payment
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
  }

  private createPaymentUrl(paymentRequest: any): string {
    const params = new URLSearchParams({
      recipient: paymentRequest.recipient,
      amount: paymentRequest.amount,
      reference: paymentRequest.reference,
      label: paymentRequest.label,
      message: paymentRequest.message,
    });

    if (paymentRequest.splToken) {
      params.append('spl-token', paymentRequest.splToken);
    }

    return `solana:${paymentRequest.recipient}?${params.toString()}`;
  }

  private validateTransaction(transaction: any, expectedAmount: number, reference?: string): boolean {
    // Add your transaction validation logic here
    // This is a simplified validation - you should implement proper checks
    
    // Check if transaction exists and was successful
    if (!transaction || transaction.meta?.err) {
      return false;
    }

    // Add more validation logic as needed
    // - Check recipient
    // - Check amount
    // - Check reference if provided
    
    return true;
  }
}
