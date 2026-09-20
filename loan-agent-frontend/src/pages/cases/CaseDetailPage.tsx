import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Phone,
  Mail,
  MessageSquare,
  Brain,
  FileText,
  Calendar,
  DollarSign,
  User
} from 'lucide-react';
import { caseService } from '@/services/caseService';
import { genaiService } from '@/services/genaiService';
import {
  Card,
  CardTitle,
  CardContent,
  Button,
  LoadingSpinner,
  StatusBadge,
  PriorityBadge,
  Modal,
  TextArea,
  Select
} from '@/components/ui';
import type { GenerateScriptRequest } from '@/types';

export const CaseDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const queryClient = useQueryClient();

  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [showScriptModal, setShowScriptModal] = useState(false);
  const [summary, setSummary] = useState('');
  const [script, setScript] = useState('');
  const [scriptScenario, setScriptScenario] = useState<string>('first_contact');
  const [scriptTone, setScriptTone] = useState<string>('professional');

  const { data: caseData, isLoading } = useQuery({
    queryKey: ['case', id],
    queryFn: () => caseService.getCase(id!),
    enabled: !!id,
  });

  const summarizeMutation = useMutation({
    mutationFn: () => genaiService.summarizeCase({ case_id: id! }),
    onSuccess: (data) => {
      setSummary(data.summary);
      setShowSummaryModal(true);
    },
  });

  const generateScriptMutation = useMutation({
    mutationFn: (request: GenerateScriptRequest) => genaiService.generateScript(request),
    onSuccess: (data) => {
      setScript(data.script);
      setShowScriptModal(true);
    },
  });

  const handleGenerateScript = () => {
    generateScriptMutation.mutate({
      case_id: id!,
      scenario: scriptScenario as any,
      tone: scriptTone as any,
    });
  };

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  if (!caseData) {
    return (
      <div className="text-center py-12">
        <p className="text-capco-gray-600">Case not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-capco-navy mb-2">{caseData.case_id}</h1>
          <div className="flex items-center gap-3">
            <StatusBadge status={caseData.status} />
            <PriorityBadge priority={caseData.priority} />
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => summarizeMutation.mutate()}
            loading={summarizeMutation.isPending}
          >
            <Brain size={16} />
            AI Summary
          </Button>
          <Button variant="primary">
            <Phone size={16} />
            Contact
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Case Information */}
          <Card>
            <CardTitle>Case Information</CardTitle>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Loan ID</p>
                  <p className="font-medium">{caseData.loan_id}</p>
                </div>
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Product</p>
                  <p className="font-medium">{caseData.loan_product}</p>
                </div>
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Principal Amount</p>
                  <p className="font-medium text-capco-navy">
                    ${caseData.principal_amount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Overdue Amount</p>
                  <p className="font-medium text-capco-red">
                    ${caseData.overdue_amount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Days Overdue</p>
                  <p className="font-medium">{caseData.overdue_days}</p>
                </div>
                <div>
                  <p className="text-sm text-capco-gray-600 mb-1">Contact Count</p>
                  <p className="font-medium">{caseData.contact_count}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Tools */}
          <Card>
            <CardTitle>AI-Powered Tools</CardTitle>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-3">
                  <p className="font-medium text-capco-navy">Generate Collection Script</p>
                  <Select
                    label="Scenario"
                    value={scriptScenario}
                    onChange={(e) => setScriptScenario(e.target.value)}
                    options={[
                      { value: 'first_contact', label: 'First Contact' },
                      { value: 'follow_up', label: 'Follow Up' },
                      { value: 'payment_reminder', label: 'Payment Reminder' },
                      { value: 'broken_promise', label: 'Broken Promise' },
                    ]}
                  />
                  <Select
                    label="Tone"
                    value={scriptTone}
                    onChange={(e) => setScriptTone(e.target.value)}
                    options={[
                      { value: 'professional', label: 'Professional' },
                      { value: 'empathetic', label: 'Empathetic' },
                      { value: 'firm', label: 'Firm' },
                      { value: 'friendly', label: 'Friendly' },
                    ]}
                  />
                  <Button
                    variant="primary"
                    className="w-full"
                    onClick={handleGenerateScript}
                    loading={generateScriptMutation.isPending}
                  >
                    <FileText size={16} />
                    Generate Script
                  </Button>
                </div>

                <div className="space-y-3">
                  <p className="font-medium text-capco-navy">Additional AI Tools</p>
                  <Button variant="secondary" className="w-full">
                    <MessageSquare size={16} />
                    Analyze Transcript
                  </Button>
                  <Button variant="secondary" className="w-full">
                    <Brain size={16} />
                    Score Willingness to Pay
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Activity Timeline */}
          <Card>
            <CardTitle>Activity Timeline</CardTitle>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-capco-blue/10 rounded-full flex items-center justify-center">
                    <Calendar className="text-capco-blue" size={20} />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-capco-navy">Case created</p>
                    <p className="text-sm text-capco-gray-600">
                      {new Date(caseData.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Customer Info */}
          <Card>
            <CardTitle>Customer</CardTitle>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-capco-blue/10 rounded-full flex items-center justify-center">
                    <User className="text-capco-blue" size={24} />
                  </div>
                  <div>
                    <p className="font-medium text-capco-navy">{caseData.customer_id}</p>
                    <p className="text-sm text-capco-gray-600">Customer ID</p>
                  </div>
                </div>
                <div className="pt-3 border-t border-capco-gray-200">
                  <Button variant="secondary" className="w-full mb-2">
                    <Phone size={16} />
                    Call
                  </Button>
                  <Button variant="secondary" className="w-full">
                    <Mail size={16} />
                    Email
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardTitle>Quick Actions</CardTitle>
            <CardContent>
              <div className="space-y-2">
                <Button variant="success" className="w-full">
                  <DollarSign size={16} />
                  Record Payment
                </Button>
                <Button variant="secondary" className="w-full">
                  Update Status
                </Button>
                <Button variant="secondary" className="w-full">
                  Add Note
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Summary Modal */}
      <Modal
        isOpen={showSummaryModal}
        onClose={() => setShowSummaryModal(false)}
        title="AI Case Summary"
        size="lg"
      >
        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-capco-gray-700">{summary}</div>
        </div>
      </Modal>

      {/* Script Modal */}
      <Modal
        isOpen={showScriptModal}
        onClose={() => setShowScriptModal(false)}
        title="Generated Collection Script"
        size="lg"
      >
        <div className="space-y-4">
          <div className="prose max-w-none">
            <div className="whitespace-pre-wrap text-capco-gray-700 p-4 bg-capco-gray-50 rounded-capco">
              {script}
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setShowScriptModal(false)}>
              Close
            </Button>
            <Button variant="primary">
              Copy Script
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
