import { AuthenticationClient, ManagementClient } from 'auth0';
import jwt from 'jsonwebtoken';
import jwksClient from 'jwks-rsa';

export class Auth0Service {
  private authClient: AuthenticationClient;
  private managementClient: ManagementClient;
  private jwksClient: jwksClient.JwksClient;

  constructor() {
    const domain = process.env.AUTH0_DOMAIN;
    const clientId = process.env.AUTH0_CLIENT_ID;
    const clientSecret = process.env.AUTH0_CLIENT_SECRET;

    if (!domain || !clientId || !clientSecret) {
      throw new Error('Auth0 configuration is missing');
    }

    this.authClient = new AuthenticationClient({
      domain,
      clientId,
      clientSecret,
    });

    this.managementClient = new ManagementClient({
      domain,
      clientId,
      clientSecret,
    });

    this.jwksClient = jwksClient({
      jwksUri: `https://${domain}/.well-known/jwks.json`
    });
  }

  async verifyToken(token: string) {
    try {
      // Decode the token to get the header
      const decoded = jwt.decode(token, { complete: true });
      
      if (!decoded || !decoded.header.kid) {
        return { success: false, error: 'Invalid token' };
      }

      // Get the signing key
      const key = await this.jwksClient.getSigningKey(decoded.header.kid);
      const signingKey = key.getPublicKey();

      // Verify the token
      const verified = jwt.verify(token, signingKey, {
        audience: process.env.AUTH0_AUDIENCE,
        issuer: `https://${process.env.AUTH0_DOMAIN}/`,
        algorithms: ['RS256']
      });

      return { success: true, user: verified };
    } catch (error) {
      console.error('Token verification error:', error);
      return { success: false, error: 'Invalid token' };
    }
  }

  async getUserById(userId: string) {
    try {
      const user = await this.managementClient.users.get({ id: userId });
      return { success: true, user };
    } catch (error) {
      console.error('Get user error:', error);
      return { success: false, error: 'User not found' };
    }
  }

  async updateUser(userId: string, userData: any) {
    try {
      const user = await this.managementClient.users.update({ id: userId }, userData);
      return { success: true, user };
    } catch (error) {
      console.error('Update user error:', error);
      return { success: false, error: 'Failed to update user' };
    }
  }
}
