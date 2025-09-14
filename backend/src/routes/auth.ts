import express from 'express';

const router = express.Router();

// Simple status endpoint since Auth0 is handled on frontend
router.get('/me', (req, res) => {
  res.status(200).json({
    message: 'Auth handled by frontend',
    backend_status: 'healthy'
  });
});

// Health check
router.get('/status', (req, res) => {
  res.status(200).json({
    status: 'OK',
    message: 'Auth service running',
    timestamp: new Date().toISOString()
  });
});

// Protected profile endpoint
router.get('/profile', (req, res) => {
  res.status(200).json({
    message: 'Profile endpoint - Auth handled by frontend',
    backend_status: 'healthy'
  });
});

export default router;
