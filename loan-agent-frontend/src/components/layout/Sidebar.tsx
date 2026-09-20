import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Briefcase,
  BarChart3,
  Brain,
  Settings,
  LogOut,
  GitBranch,
  BookOpen
} from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuthStore();

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/cases', icon: Briefcase, label: 'Cases' },
    { to: '/workflows', icon: GitBranch, label: 'Workflows' },
    { to: '/rules', icon: BookOpen, label: 'Rules Engine' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/genai', icon: Brain, label: 'GenAI Tools' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="flex flex-col h-full bg-capco-navy text-white w-64">
      {/* Logo */}
      <div className="p-6 border-b border-capco-blue">
        <h1 className="text-2xl font-bold text-white">Capco</h1>
        <p className="text-sm text-capco-lightBlue">Loan Collection Agent</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive
                ? 'flex items-center gap-3 px-4 py-3 bg-capco-blue rounded-capco text-white font-medium'
                : 'flex items-center gap-3 px-4 py-3 text-capco-gray-200 hover:bg-capco-blue/20 rounded-capco transition-colors'
            }
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="p-4 border-t border-capco-blue">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 rounded-full bg-capco-blue flex items-center justify-center">
            <span className="text-sm font-medium">
              {user?.full_name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name}</p>
            <p className="text-xs text-capco-gray-300 truncate">{user?.role}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 w-full px-4 py-2 text-capco-gray-300 hover:bg-capco-blue/20 rounded-capco transition-colors"
        >
          <LogOut size={16} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};
