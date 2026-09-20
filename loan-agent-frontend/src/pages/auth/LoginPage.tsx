import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button, Input } from '@/components/ui';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      // Error handled by store
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-capco-navy to-capco-blue flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-capco shadow-capco-xl p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-capco-navy mb-2">Capco</h1>
          <p className="text-capco-gray-600">Loan Collection Agent</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            autoFocus
          />

          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && (
            <div className="p-3 bg-red-50 border border-capco-red rounded-capco">
              <p className="text-sm text-capco-red">{error}</p>
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            className="w-full"
            loading={isLoading}
          >
            Sign In
          </Button>
        </form>

        {/* Demo credentials */}
        <div className="mt-6 p-4 bg-capco-gray-50 rounded-capco">
          <p className="text-xs text-capco-gray-600 mb-2 font-medium">Demo Credentials:</p>
          <p className="text-xs text-capco-gray-600">Admin: admin / admin123</p>
          <p className="text-xs text-capco-gray-600">Collector: collector1 / admin123</p>
        </div>
      </div>
    </div>
  );
};
