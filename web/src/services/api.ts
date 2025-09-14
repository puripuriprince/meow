import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3001';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth0 API calls
export const authAPI = {
  // Login with Auth0 token
  login: async (token: string) => {
    const response = await apiClient.post('/api/auth/login', { token });
    return response.data;
  },

  // Verify Auth0 token
  verifyToken: async (token: string) => {
    const response = await apiClient.post('/api/auth/verify', { token });
    return response.data;
  },

  // Get user profile
  getUserProfile: async (userId: string, token: string) => {
    const response = await apiClient.get(`/api/auth/profile/${userId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Update user profile
  updateUserProfile: async (userId: string, userData: any, token: string) => {
    const response = await apiClient.put(`/api/auth/profile/${userId}`, userData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },
};

// Solana Pay API calls
export const solanaPayAPI = {
  // Create SOL payment request
  createPayment: async (paymentData: {
    amount: number;
    label: string;
    message?: string;
  }, token: string) => {
    const response = await apiClient.post('/api/solana-pay/create-payment', paymentData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Create token payment request
  createTokenPayment: async (paymentData: {
    tokenMint: string;
    amount: number;
    decimals: number;
    label: string;
    message?: string;
  }, token: string) => {
    const response = await apiClient.post('/api/solana-pay/create-token-payment', paymentData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Verify payment
  verifyPayment: async (verificationData: {
    signature: string;
    expectedAmount: number;
    reference?: string;
  }, token: string) => {
    const response = await apiClient.post('/api/solana-pay/verify-payment', verificationData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Get transaction status
  getTransactionStatus: async (signature: string, token: string) => {
    const response = await apiClient.get(`/api/solana-pay/transaction-status/${signature}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/api/solana-pay/health');
    return response.data;
  },
};

// General API calls
export const generalAPI = {
  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
