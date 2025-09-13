import { AuthenticationClient, ManagementClient } from 'auth0';

export class Auth0Service {
  private authClient: AuthenticationClient;
  private managementClient: ManagementClient;

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
      scope: 'read:users update:users create:users delete:users'
    });
  }

  async verifyToken(token: string) {
    try {
      const user = await this.authClient.getProfile(token);
      return { success: true, user };
    } catch (error) {
      return { success: false, error: 'Invalid token' };
    }
  }

  async getUserById(userId: string) {
    try {
      const user = await this.managementClient.getUser({ id: userId });
      return { success: true, user };
    } catch (error) {
      return { success: false, error: 'User not found' };
    }
  }

  async updateUser(userId: string, userData: any) {
    try {
      const user = await this.managementClient.updateUser({ id: userId }, userData);
      return { success: true, user };
    } catch (error) {
      return { success: false, error: 'Failed to update user' };
    }
  }
}
