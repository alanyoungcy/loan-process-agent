import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Brain, FileText, MessageSquare, TrendingUp } from 'lucide-react';
import { genaiService } from '@/services/genaiService';
import {
  Card,
  CardTitle,
  CardContent,
  Button,
  TextArea,
  Select,
  Input,
  LoadingSpinner,
} from '@/components/ui';

export const GenAIPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'script' | 'intent' | 'willingness'>('script');

  // Script generation
  const [caseId, setCaseId] = useState('');
  const [scenario, setScenario] = useState('first_contact');
  const [tone, setTone] = useState('professional');
  const [generatedScript, setGeneratedScript] = useState('');

  // Intent analysis
  const [transcript, setTranscript] = useState('');
  const [intentResult, setIntentResult] = useState<any>(null);

  // Willingness scoring
  const [scoreCaseId, setScoreCaseId] = useState('');
  const [willingnessResult, setWillingnessResult] = useState<any>(null);

  const scriptMutation = useMutation({
    mutationFn: genaiService.generateScript,
    onSuccess: (data) => {
      setGeneratedScript(data.script);
    },
  });

  const intentMutation = useMutation({
    mutationFn: genaiService.analyzeIntent,
    onSuccess: (data) => {
      setIntentResult(data);
    },
  });

  const willingsnessMutation = useMutation({
    mutationFn: genaiService.scoreWillingness,
    onSuccess: (data) => {
      setWillingnessResult(data);
    },
  });

  const handleGenerateScript = () => {
    scriptMutation.mutate({
      case_id: caseId,
      scenario: scenario as any,
      tone: tone as any,
    });
  };

  const handleAnalyzeIntent = () => {
    intentMutation.mutate({ transcript });
  };

  const handleScoreWillingness = () => {
    willingsnessMutation.mutate({ case_id: scoreCaseId });
  };

  const tabs = [
    { id: 'script', label: 'Script Generator', icon: FileText },
    { id: 'intent', label: 'Intent Analysis', icon: MessageSquare },
    { id: 'willingness', label: 'Willingness Score', icon: TrendingUp },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-capco-navy mb-2">GenAI Tools</h1>
        <p className="text-capco-gray-600">
          AI-powered tools to enhance your collection process
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-capco-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'border-capco-blue text-capco-blue font-medium'
                : 'border-transparent text-capco-gray-600 hover:text-capco-navy'
            }`}
          >
            <tab.icon size={20} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Script Generator */}
      {activeTab === 'script' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardTitle>Generate Collection Script</CardTitle>
            <CardContent>
              <div className="space-y-4">
                <Input
                  label="Case ID"
                  value={caseId}
                  onChange={(e) => setCaseId(e.target.value)}
                  placeholder="Enter case ID"
                  required
                />

                <Select
                  label="Scenario"
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  options={[
                    { value: 'first_contact', label: 'First Contact' },
                    { value: 'follow_up', label: 'Follow Up' },
                    { value: 'payment_reminder', label: 'Payment Reminder' },
                    { value: 'broken_promise', label: 'Broken Promise' },
                    { value: 'dispute_resolution', label: 'Dispute Resolution' },
                    { value: 'payment_plan_discussion', label: 'Payment Plan Discussion' },
                  ]}
                />

                <Select
                  label="Tone"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
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
                  loading={scriptMutation.isPending}
                  disabled={!caseId}
                >
                  <Brain size={16} />
                  Generate Script
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardTitle>Generated Script</CardTitle>
            <CardContent>
              {scriptMutation.isPending ? (
                <LoadingSpinner size="md" />
              ) : generatedScript ? (
                <div className="space-y-4">
                  <div className="p-4 bg-capco-gray-50 rounded-capco whitespace-pre-wrap text-sm">
                    {generatedScript}
                  </div>
                  <Button variant="secondary" className="w-full">
                    Copy to Clipboard
                  </Button>
                </div>
              ) : (
                <p className="text-capco-gray-500 text-center py-8">
                  Generated script will appear here
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Intent Analysis */}
      {activeTab === 'intent' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardTitle>Analyze Customer Intent</CardTitle>
            <CardContent>
              <div className="space-y-4">
                <TextArea
                  label="Conversation Transcript"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  placeholder="Paste the conversation transcript here..."
                  rows={10}
                  required
                />

                <Button
                  variant="primary"
                  className="w-full"
                  onClick={handleAnalyzeIntent}
                  loading={intentMutation.isPending}
                  disabled={!transcript}
                >
                  <MessageSquare size={16} />
                  Analyze Intent
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardTitle>Analysis Results</CardTitle>
            <CardContent>
              {intentMutation.isPending ? (
                <LoadingSpinner size="md" />
              ) : intentResult ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-capco-gray-600 mb-1">Intent</p>
                    <p className="text-lg font-semibold text-capco-navy capitalize">
                      {intentResult.intent.replace(/_/g, ' ')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-capco-gray-600 mb-1">Sentiment</p>
                    <p className="text-lg font-semibold capitalize">
                      {intentResult.sentiment}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-capco-gray-600 mb-1">Willingness to Pay Score</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-capco-gray-200 rounded-full h-2">
                        <div
                          className="bg-capco-green h-2 rounded-full"
                          style={{ width: `${intentResult.willingness_to_pay_score * 10}%` }}
                        />
                      </div>
                      <span className="font-semibold">
                        {intentResult.willingness_to_pay_score}/10
                      </span>
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-capco-gray-600 mb-2">Key Points</p>
                    <ul className="space-y-1">
                      {intentResult.key_points.map((point: string, i: number) => (
                        <li key={i} className="text-sm text-capco-gray-700 flex items-start gap-2">
                          <span className="text-capco-blue">•</span>
                          {point}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm text-capco-gray-600 mb-2">Recommended Actions</p>
                    <ul className="space-y-1">
                      {intentResult.recommended_actions.map((action: string, i: number) => (
                        <li key={i} className="text-sm text-capco-gray-700 flex items-start gap-2">
                          <span className="text-capco-green">✓</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <p className="text-capco-gray-500 text-center py-8">
                  Analysis results will appear here
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Willingness Scoring */}
      {activeTab === 'willingness' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardTitle>Score Willingness to Pay</CardTitle>
            <CardContent>
              <div className="space-y-4">
                <Input
                  label="Case ID"
                  value={scoreCaseId}
                  onChange={(e) => setScoreCaseId(e.target.value)}
                  placeholder="Enter case ID"
                  required
                />

                <Button
                  variant="primary"
                  className="w-full"
                  onClick={handleScoreWillingness}
                  loading={willingsnessMutation.isPending}
                  disabled={!scoreCaseId}
                >
                  <TrendingUp size={16} />
                  Calculate Score
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardTitle>Willingness Score</CardTitle>
            <CardContent>
              {willingsnessMutation.isPending ? (
                <LoadingSpinner size="md" />
              ) : willingnessResult ? (
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="inline-flex items-center justify-center w-32 h-32 rounded-full bg-capco-blue/10 mb-4">
                      <span className="text-4xl font-bold text-capco-blue">
                        {willingnessResult.score}
                      </span>
                    </div>
                    <p className="text-sm text-capco-gray-600">
                      Confidence: {(willingnessResult.confidence * 100).toFixed(0)}%
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-capco-gray-700 mb-3">
                      Contributing Factors
                    </p>
                    <div className="space-y-3">
                      {willingnessResult.factors.map((factor: any, i: number) => (
                        <div key={i} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="text-capco-gray-700">{factor.factor}</span>
                            <span className="font-medium">
                              {factor.impact > 0 ? '+' : ''}
                              {factor.impact}
                            </span>
                          </div>
                          <p className="text-xs text-capco-gray-600">{factor.explanation}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-4 bg-capco-blue/10 rounded-capco">
                    <p className="text-sm font-medium text-capco-navy mb-1">Recommendation</p>
                    <p className="text-sm text-capco-gray-700">
                      {willingnessResult.recommendation}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-capco-gray-500 text-center py-8">
                  Willingness score will appear here
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};
