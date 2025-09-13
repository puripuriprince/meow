import express from 'express';
import { Auth0Service } from '../services/auth0.service';

const router = express.Router();
const auth0Service = new Auth0Service();

// Login endpoint
router.post('/login', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Token is required' });
    }

    const result = await auth0Service.verifyToken(token);

    if (result.success) {
      res.status(200).json({
        message: 'Login successful',
        user: result.user
      });
    } else {
      res.status(401).json({ error: result.error });
    }
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get user profile endpoint
router.get('/profile/:userId', async (req, res) => {
  try {
    const { userId } = req.params;

    const result = await auth0Service.getUserById(userId);

    if (result.success) {
      res.status(200).json({
        message: 'Profile retrieved successfully',
        user: result.user
      });
    } else {
      res.status(404).json({ error: result.error });
    }
  } catch (error) {
    console.error('Profile retrieval error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user profile endpoint
router.put('/profile/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const userData = req.body;

    const result = await auth0Service.updateUser(userId, userData);

    if (result.success) {
      res.status(200).json({
        message: 'Profile updated successfully',
        user: result.user
      });
    } else {
      res.status(400).json({ error: result.error });
    }
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Verify token endpoint
router.post('/verify', async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ error: 'Token is required' });
    }

    const result = await auth0Service.verifyToken(token);

    if (result.success) {
      res.status(200).json({
        valid: true,
        user: result.user
      });
    } else {
      res.status(401).json({
        valid: false,
        error: result.error
      });
    }
  } catch (error) {
    console.error('Token verification error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
