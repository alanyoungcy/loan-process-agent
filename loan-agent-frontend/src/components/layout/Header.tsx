import React from 'react';
import { Bell, Search } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="bg-white border-b border-capco-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-capco-gray-400" size={20} />
            <input
              type="search"
              placeholder="Search cases, customers..."
              className="w-full pl-10 pr-4 py-2 border border-capco-gray-300 rounded-capco focus:outline-none focus:ring-2 focus:ring-capco-blue"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <button className="relative p-2 text-capco-gray-600 hover:bg-capco-gray-100 rounded-capco transition-colors">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-capco-red rounded-full" />
          </button>
        </div>
      </div>
    </header>
  );
};
