import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './store/authStore';
import { MainLayout } from './components/layout/MainLayout';
import { LoginPage } from './pages/auth/LoginPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { CasesListPage } from './pages/cases/CasesListPage';
import { CaseDetailPage } from './pages/cases/CaseDetailPage';
import { GenAIPage } from './pages/genai/GenAIPage';
import { AnalyticsPage } from './pages/analytics/AnalyticsPage';
import { SettingsPage } from './pages/settings/SettingsPage';
import { WorkflowsPage } from './pages/workflows/WorkflowsPage';
import { WorkflowManagementPage } from './pages/workflows/WorkflowManagementPage';
import { DmnDesignerPage } from './pages/dmn/DmnDesignerPage';
import { RulesPage } from './pages/rules/RulesPage';

const queryClient = new QueryClient();

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  const initAuth = useAuthStore((state) => state.initAuth);

  useEffect(() => {
    initAuth();
  }, [initAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="cases" element={<CasesListPage />} />
            <Route path="cases/:id" element={<CaseDetailPage />} />
            <Route path="workflows" element={<WorkflowsPage />} />
            <Route path="workflows/designer" element={<WorkflowManagementPage />} />
            <Route path="dmn/designer" element={<DmnDesignerPage />} />
            <Route path="rules" element={<RulesPage />} />
            <Route path="genai" element={<GenAIPage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
