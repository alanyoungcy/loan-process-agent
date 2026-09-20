import React, { useState, useEffect } from 'react';
import { Bot, Brain, Flask, Shield, Activity, AlertCircle, TrendingUp } from 'lucide-react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface AIMetrics {
  chatbot: {
    sessions_24h: number;
    resolution_rate: number;
    avg_duration_minutes: number;
  };
  multi_agent: {
    debates_24h: number;
    avg_confidence: number;
    acceptance_rate: number;
  };
  trust_gate: {
    approval_rate: number;
    reviews_pending: number;
    blocked_count: number;
  };
  ab_testing: {
    active_experiments: number;
    experiments_concluding: number;
    overall_success_rate: number;
  };
  ai_actions: {
    executed_24h: number;
    reviewed_24h: number;
    accuracy: number;
  };
  alerts: {
    pending: number;
    critical: number;
  };
}

interface ActiveSession {
  id: string;
  type: 'chatbot' | 'debate' | 'review';
  case_id: string;
  status: string;
  metadata: any;
  trust_gate?: any;
}

export const AICommandCenter: React.FC = () => {
  const [metrics, setMetrics] = useState<AIMetrics | null>(null);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    fetchActiveSessions();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      fetchMetrics();
      fetchActiveSessions();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/v1/ai/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchActiveSessions = async () => {
    try {
      const response = await fetch('/api/v1/ai/active-sessions');
      const data = await response.json();
      setActiveSessions(data);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch active sessions:', error);
      setIsLoading(false);
    }
  };

  if (isLoading || !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Activity className="w-8 h-8 text-blue-600" />
        <div>
          <h1 className="text-2xl font-bold">🤖 AI Command Center</h1>
          <p className="text-gray-600">Monitor and manage all AI operations</p>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Chatbot Metrics */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold">Chatbot</h3>
            </div>
            <Badge color="green">Active</Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Sessions (24h)</span>
              <span className="text-2xl font-bold">{metrics.chatbot.sessions_24h}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Resolution Rate</span>
              <span className="text-lg font-semibold text-green-600">
                {(metrics.chatbot.resolution_rate * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Duration</span>
              <span className="text-sm font-medium">
                {metrics.chatbot.avg_duration_minutes.toFixed(1)}m
              </span>
            </div>
          </div>
        </Card>

        {/* Multi-Agent Metrics */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              <h3 className="font-semibold">Debates</h3>
            </div>
            <Badge color="purple">Active</Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Debates (24h)</span>
              <span className="text-2xl font-bold">{metrics.multi_agent.debates_24h}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg Confidence</span>
              <span className="text-lg font-semibold text-purple-600">
                {(metrics.multi_agent.avg_confidence * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Acceptance Rate</span>
              <span className="text-sm font-medium">
                {(metrics.multi_agent.acceptance_rate * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </Card>

        {/* Trust Gate Metrics */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-600" />
              <h3 className="font-semibold">Trust Gate</h3>
            </div>
            <Badge color="green">Operational</Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Approval Rate</span>
              <span className="text-2xl font-bold text-green-600">
                {(metrics.trust_gate.approval_rate * 100).toFixed(0)}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Reviews Pending</span>
              <span className="text-lg font-semibold text-yellow-600">
                {metrics.trust_gate.reviews_pending}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Blocked (24h)</span>
              <span className="text-sm font-medium text-red-600">
                {metrics.trust_gate.blocked_count}
              </span>
            </div>
          </div>
        </Card>

        {/* A/B Testing Metrics */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Flask className="w-5 h-5 text-orange-600" />
              <h3 className="font-semibold">A/B Tests</h3>
            </div>
            <Badge color="orange">
              {metrics.ab_testing.active_experiments} Active
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Active</span>
              <span className="text-2xl font-bold">
                {metrics.ab_testing.active_experiments}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Concluding Soon</span>
              <span className="text-lg font-semibold text-orange-600">
                {metrics.ab_testing.experiments_concluding}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Success Rate</span>
              <span className="text-sm font-medium">
                {(metrics.ab_testing.overall_success_rate * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </Card>

        {/* AI Actions Metrics */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold">AI Actions</h3>
            </div>
            <Badge color="blue">Tracking</Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Executed (24h)</span>
              <span className="text-2xl font-bold">{metrics.ai_actions.executed_24h}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Reviewed (24h)</span>
              <span className="text-lg font-semibold text-yellow-600">
                {metrics.ai_actions.reviewed_24h}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Accuracy</span>
              <span className="text-sm font-medium text-green-600">
                {(metrics.ai_actions.accuracy * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </Card>

        {/* Alerts */}
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <h3 className="font-semibold">Alerts</h3>
            </div>
            <Badge color={metrics.alerts.critical > 0 ? 'red' : 'gray'}>
              {metrics.alerts.pending} Total
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Pending</span>
              <span className="text-2xl font-bold text-yellow-600">
                {metrics.alerts.pending}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Critical</span>
              <span className="text-lg font-semibold text-red-600">
                {metrics.alerts.critical}
              </span>
            </div>
            {metrics.alerts.pending > 0 && (
              <Button
                variant="outline"
                size="sm"
                className="w-full text-red-600 border-red-600 hover:bg-red-50"
              >
                View Alerts
              </Button>
            )}
          </div>
        </Card>
      </div>

      {/* Active Sessions */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Active AI Sessions</h2>
        <div className="space-y-3">
          {activeSessions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No active sessions at the moment
            </div>
          ) : (
            activeSessions.map((session) => (
              <ActiveSessionCard key={session.id} session={session} />
            ))
          )}
        </div>
      </Card>

      {/* Performance Trends */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Performance Trends</h2>
        <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-500">
          <TrendingUp className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>AI Acceptance Rate trend chart would go here</p>
          <p className="text-sm mt-1">Last 7 Days</p>
        </div>
      </Card>
    </div>
  );
};

const ActiveSessionCard: React.FC<{ session: ActiveSession }> = ({ session }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'chatbot':
        return <Bot className="w-5 h-5 text-blue-600" />;
      case 'debate':
        return <Brain className="w-5 h-5 text-purple-600" />;
      case 'review':
        return <Shield className="w-5 h-5 text-yellow-600" />;
      default:
        return <Activity className="w-5 h-5 text-gray-600" />;
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'chatbot':
        return 'Customer Chat';
      case 'debate':
        return 'Strategy Debate';
      case 'review':
        return 'Script Review';
      default:
        return 'AI Session';
    }
  };

  const getTrustGateBadge = (trustGate?: any) => {
    if (!trustGate) return null;

    const colors: Record<string, string> = {
      auto_execute: 'green',
      human_review: 'yellow',
      escalate: 'orange',
      block: 'red',
    };

    return (
      <Badge color={colors[trustGate.decision] || 'gray'}>
        {trustGate.decision === 'auto_execute' ? '✅ Low Risk' : '🟡 Review Required'}
      </Badge>
    );
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          {getIcon(session.type)}
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="font-medium">{getTypeLabel(session.type)}</span>
              <span className="text-gray-500">-</span>
              <span className="text-sm text-gray-600">{session.case_id}</span>
            </div>
            <div className="text-sm text-gray-600">{session.status}</div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {getTrustGateBadge(session.trust_gate)}
          <Button variant="outline" size="sm">
            View
          </Button>
          {session.type === 'chatbot' && (
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
              Take Over
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};
