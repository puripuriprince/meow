import express from 'express';
import { SolanaPayService } from '../services/solana-pay.service';

const router = express.Router();
const solanaPayService = new SolanaPayService();

// Create SOL payment request
router.post('/create-payment', async (req, res) => {
  try {
    const { amount, label, message } = req.body;

    if (!amount || !label) {
      return res.status(400).json({ 
        error: 'Amount and label are required' 
      });
    }

    if (amount <= 0) {
      return res.status(400).json({ 
        error: 'Amount must be greater than 0' 
      });
    }

    const result = await solanaPayService.createPaymentRequest(amount, label, message);

    if (result.success) {
      res.status(200).json({
        message: 'Payment request created successfully',
        paymentRequest: result.paymentRequest,
        paymentUrl: result.paymentUrl
      });
    } else {
      res.status(500).json({ error: result.error });
    }
  } catch (error) {
    console.error('Create payment error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create token payment request
router.post('/create-token-payment', async (req, res) => {
  try {
    const { tokenMint, amount, decimals, label, message } = req.body;

    if (!tokenMint || !amount || !decimals || !label) {
      return res.status(400).json({ 
        error: 'Token mint, amount, decimals, and label are required' 
      });
    }

    if (amount <= 0) {
      return res.status(400).json({ 
        error: 'Amount must be greater than 0' 
      });
    }

    const result = await solanaPayService.createTokenPaymentRequest(
      tokenMint, 
      amount, 
      decimals, 
      label, 
      message
    );

    if (result.success) {
      res.status(200).json({
        message: 'Token payment request created successfully',
        paymentRequest: result.paymentRequest,
        paymentUrl: result.paymentUrl
      });
    } else {
      res.status(500).json({ error: result.error });
    }
  } catch (error) {
    console.error('Create token payment error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Verify payment
router.post('/verify-payment', async (req, res) => {
  try {
    const { signature, expectedAmount, reference } = req.body;

    if (!signature || !expectedAmount) {
      return res.status(400).json({ 
        error: 'Signature and expected amount are required' 
      });
    }

    const result = await solanaPayService.verifyPayment(signature, expectedAmount, reference);

    if (result.success) {
      res.status(200).json({
        message: 'Payment verification completed',
        verified: result.verified,
        transaction: result.transaction
      });
    } else {
      res.status(400).json({ error: result.error });
    }
  } catch (error) {
    console.error('Verify payment error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get transaction status
router.get('/transaction-status/:signature', async (req, res) => {
  try {
    const { signature } = req.params;

    if (!signature) {
      return res.status(400).json({ 
        error: 'Transaction signature is required' 
      });
    }

    const result = await solanaPayService.getTransactionStatus(signature);

    if (result.success) {
      res.status(200).json({
        message: 'Transaction status retrieved successfully',
        status: result.status,
        confirmed: result.confirmed
      });
    } else {
      res.status(400).json({ error: result.error });
    }
  } catch (error) {
    console.error('Transaction status error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Health check for Solana connection
router.get('/health', async (req, res) => {
  try {
    // You could add a simple connection test here
    res.status(200).json({
      message: 'Solana Pay service is running',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Solana Pay health check error:', error);
    res.status(500).json({ error: 'Service unavailable' });
  }
});

export default router;
