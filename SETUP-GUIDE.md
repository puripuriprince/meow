# 🚀 Meow - Complete Setup Guide

## 🔧 Quick Setup (No Configuration Needed)

Your application is now ready! Here's what I've set up for you:

### ✅ What's Working Now

1. **Frontend (Next.js)**: Running on `http://localhost:3000`

   - Modern UI with Radix UI components
   - Auth0 authentication ready
   - Solana wallet integration
   - Dashboard for authenticated users

2. **Backend (Express)**: Ready to run on `http://localhost:3001`

   - Auth0 JWT verification
   - Solana Pay API endpoints
   - CORS enabled for frontend

3. **Authentication Flow**:

   - Click "Sign In" to authenticate with Auth0
   - Access dashboard after login
   - Connect Solana wallet for payments

4. **Payment Flow**:
   - Connect wallet → Sign in → Go to dashboard → Make payment

## 🎯 To Get Everything Working:

### 1. Set Up Auth0 (Optional - for production)

If you want to use real Auth0 authentication:

1. Go to [Auth0 Dashboard](https://auth0.com/)
2. Create a new application (Single Page Application)
3. Update these files:

**Frontend (.env.local):**

```env
NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.us.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id
NEXT_PUBLIC_AUTH0_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_AUTH0_AUDIENCE=your-api-audience
```

**Backend (.env):**

```env
AUTH0_DOMAIN=your-domain.us.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=your-api-audience
```

### 2. Set Up Solana Wallet (Optional - for real payments)

Replace the merchant wallet in backend `.env`:

```env
MERCHANT_WALLET=your-actual-solana-wallet-address
```

## 🖥️ How to Run

### Start Backend:

```bash
cd backend
npm run dev
```

### Start Frontend:

```bash
cd web
npm run dev
```

Visit: `http://localhost:3000`

## 🔥 Features

### Authentication

- ✅ Auth0 login/logout
- ✅ Protected dashboard
- ✅ User profile display
- ✅ JWT token verification

### Solana Integration

- ✅ Wallet connection (Phantom, Solflare, Torus)
- ✅ Payment form
- ✅ Transaction verification
- ✅ Payment history (placeholder)

### UI/UX

- ✅ Modern design with animations
- ✅ Responsive layout
- ✅ Loading states
- ✅ Error handling
- ✅ Success notifications

## 📁 Project Structure

```
meow/
├── web/                    # Next.js Frontend
│   ├── src/
│   │   ├── app/           # Pages
│   │   ├── components/    # UI Components
│   │   ├── contexts/      # Auth0 & Solana providers
│   │   └── services/      # API calls
│   └── .env.local         # Frontend config
│
├── backend/               # Express Backend
│   ├── src/
│   │   ├── routes/       # API endpoints
│   │   └── services/     # Business logic
│   └── .env              # Backend config
│
└── README.md             # This file
```

## 🚀 API Endpoints

### Authentication

- `POST /api/auth/login` - Login with Auth0
- `POST /api/auth/verify` - Verify token
- `GET /api/auth/profile/:id` - Get user profile

### Solana Pay

- `POST /api/solana-pay/create-payment` - Create payment
- `POST /api/solana-pay/verify-payment` - Verify payment
- `GET /api/solana-pay/transaction-status/:sig` - Check status

## 🎨 What's Included

### Frontend Components

- `AuthButton` - Login/logout with dropdown
- `WalletButton` - Solana wallet connection
- `PaymentForm` - Complete payment interface
- `Dashboard` - User dashboard with payments

### Backend Services

- `Auth0Service` - JWT verification & user management
- `SolanaPayService` - Payment processing
- Complete error handling & validation

## 🔧 Development Notes

1. **Environment Files**: Both frontend and backend have example env files
2. **CORS**: Configured for local development
3. **TypeScript**: Full type safety throughout
4. **Error Handling**: Comprehensive error boundaries
5. **Loading States**: Proper UX during async operations

## 🚀 Going Live

When ready for production:

1. Update Auth0 domains and URLs
2. Set up real Solana wallet
3. Configure production environment variables
4. Deploy backend and frontend
5. Update CORS settings for production domains

---

**Everything is connected and ready to go! 🎉**

Just start both servers and visit localhost:3000 to see your app in action!
