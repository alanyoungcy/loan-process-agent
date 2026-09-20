import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import { caseService } from '@/services/caseService';
import { Card, Input, Select, LoadingSpinner, StatusBadge, PriorityBadge } from '@/components/ui';
import type { CaseStatus } from '@/types';

export const CasesListPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  const { data: cases, isLoading } = useQuery({
    queryKey: ['cases', statusFilter],
    queryFn: () => caseService.getCases({
      status: statusFilter || undefined,
      limit: 100
    }),
  });

  const filteredCases = cases?.filter(c =>
    c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.customer_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-capco-navy mb-2">Cases</h1>
          <p className="text-capco-gray-600">Manage and track collection cases</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-capco-gray-400" size={20} />
              <input
                type="search"
                placeholder="Search by case ID or customer..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 input"
              />
            </div>
          </div>
          <div className="w-full md:w-64">
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={[
                { value: '', label: 'All Status' },
                { value: 'new', label: 'New' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'contacted', label: 'Contacted' },
                { value: 'closed', label: 'Closed' },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Cases Table */}
      <Card padding="none">
        {isLoading ? (
          <LoadingSpinner size="lg" className="py-12" />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-capco-gray-50 border-b border-capco-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Case ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Customer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Overdue Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Days Overdue
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-capco-gray-600 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-capco-gray-200">
                {filteredCases?.map((caseItem) => (
                  <tr
                    key={caseItem.id}
                    onClick={() => navigate(`/cases/${caseItem.id}`)}
                    className="hover:bg-capco-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-capco-navy">{caseItem.case_id}</div>
                      <div className="text-sm text-capco-gray-500">{caseItem.loan_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-capco-gray-900">{caseItem.customer_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-semibold text-capco-red">
                        ${caseItem.overdue_amount.toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-capco-gray-900">{caseItem.overdue_days}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <PriorityBadge priority={caseItem.priority} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={caseItem.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
