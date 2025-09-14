# Meow Backend API

This is the backend API for the Meow application, providing authentication through Auth0 and payment processing through Solana Pay.

## Setup

1. Install dependencies:

```bash
cd backend
npm install
```

2. Copy the environment configuration:

```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:

   - `AUTH0_DOMAIN`: Your Auth0 domain
   - `AUTH0_CLIENT_ID`: Your Auth0 client ID
   - `AUTH0_CLIENT_SECRET`: Your Auth0 client secret
   - `AUTH0_AUDIENCE`: Your Auth0 API audience
   - `SOLANA_NETWORK`: Solana network (mainnet-beta, testnet, devnet)
   - `SOLANA_RPC_URL`: Solana RPC endpoint URL
   - `MERCHANT_WALLET`: Your merchant wallet public key

4. Start the development server:

```bash
npm run dev
```

## API Endpoints

### Health Check

- **GET** `/health` - Check if the server is running

### Auth0 Authentication

#### Login

- **POST** `/api/auth/login`
- Body: `{ "token": "auth0_access_token" }`
- Response: User profile and login status

#### Verify Token

- **POST** `/api/auth/verify`
- Body: `{ "token": "auth0_access_token" }`
- Response: Token validity and user info

#### Get User Profile

- **GET** `/api/auth/profile/:userId`
- Response: User profile information

#### Update User Profile

- **PUT** `/api/auth/profile/:userId`
- Body: User data to update
- Response: Updated user profile

### Solana Pay

#### Create SOL Payment Request

- **POST** `/api/solana-pay/create-payment`
- Body: `{ "amount": 0.1, "label": "Product Name", "message": "Optional message" }`
- Response: Payment request details and Solana Pay URL

#### Create Token Payment Request

- **POST** `/api/solana-pay/create-token-payment`
- Body: `{ "tokenMint": "token_mint_address", "amount": 100, "decimals": 6, "label": "Product Name", "message": "Optional message" }`
- Response: Token payment request details and Solana Pay URL

#### Verify Payment

- **POST** `/api/solana-pay/verify-payment`
- Body: `{ "signature": "transaction_signature", "expectedAmount": 0.1, "reference": "payment_reference" }`
- Response: Payment verification status

#### Get Transaction Status

- **GET** `/api/solana-pay/transaction-status/:signature`
- Response: Transaction confirmation status

#### Health Check

- **GET** `/api/solana-pay/health`
- Response: Solana Pay service status

## Development

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Production

```bash
npm start
```

## Environment Variables

| Variable              | Description                          | Required |
| --------------------- | ------------------------------------ | -------- |
| `NODE_ENV`            | Environment (development/production) | No       |
| `PORT`                | Server port (default: 3001)          | No       |
| `AUTH0_DOMAIN`        | Auth0 domain                         | Yes      |
| `AUTH0_CLIENT_ID`     | Auth0 client ID                      | Yes      |
| `AUTH0_CLIENT_SECRET` | Auth0 client secret                  | Yes      |
| `AUTH0_AUDIENCE`      | Auth0 API audience                   | Yes      |
| `SOLANA_NETWORK`      | Solana network                       | No       |
| `SOLANA_RPC_URL`      | Solana RPC URL                       | No       |
| `MERCHANT_WALLET`     | Merchant wallet address              | Yes      |

## Project Structure

```
backend/
├── src/
│   ├── routes/
│   │   ├── auth.ts          # Auth0 authentication routes
│   │   └── solana-pay.ts    # Solana Pay routes
│   ├── services/
│   │   ├── auth0.service.ts    # Auth0 service logic
│   │   └── solana-pay.service.ts # Solana Pay service logic
│   ├── middleware/          # Express middleware
│   └── index.ts            # Main application entry point
├── dist/                   # Compiled JavaScript output
├── package.json
├── tsconfig.json
└── .env.example
```
