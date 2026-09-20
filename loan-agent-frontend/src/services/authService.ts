import api from './api';
import type { User, LoginRequest, AuthResponse } from '@/types';

export const authService = {
  async login(credentials: LoginRequest): Promise<{ user: User; token: string }> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const { data } = await api.post<AuthResponse>('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    // Store token
    localStorage.setItem('access_token', data.access_token);

    // Get user info
    const user = await this.getCurrentUser();
    localStorage.setItem('user', JSON.stringify(user));

    return { user, token: data.access_token };
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<User>('/api/v1/auth/me');
    return data;
  },

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};
