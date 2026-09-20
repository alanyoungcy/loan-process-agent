import React, { useState } from 'react';
import { Users, Brain, CheckCircle, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { TrustGateBadge } from './TrustGateBadge';

interface AgentProposal {
  agent: string;
  expertise: string;
  proposal: string;
  timestamp: string;
}

interface AgentCritique {
  critic: string;
  proposal_agent: string;
  critique: string;
  timestamp: string;
}

interface Consensus {
  strategy: string;
  confidence: number;
  num_agents: number;
  agreement_level: number;
}

interface DebateResult {
  case_id: string;
  debate_rounds: number;
  proposals: AgentProposal[];
  critiques: AgentCritique[];
  consensus: Consensus;
  confidence: number;
  debated_at: string;
  trust_gate_evaluation?: any;
}

interface MultiAgentDebateProps {
  caseId: string;
  caseData?: {
    overdue_amount: number;
    overdue_days: number;
    status: string;
    contact_count?: number;
    priority?: number;
  };
  onAccept?: (consensus: Consensus) => void;
  onReject?: () => void;
}

export const MultiAgentDebate: React.FC<MultiAgentDebateProps> = ({
  caseId,
  caseData,
  onAccept,
  onReject,
}) => {
  const [debateResult, setDebateResult] = useState<DebateResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [showCritiques, setShowCritiques] = useState(false);

  const agentConfig: Record<
    string,
    { icon: string; color: string; bgColor: string }
  > = {
    'Compliance Officer': { icon: '🛡️', color: 'text-blue-700', bgColor: 'bg-blue-50' },
    'Customer Relations Expert': { icon: '😊', color: 'text-green-700', bgColor: 'bg-green-50' },
    'Data Analyst': { icon: '📊', color: 'text-purple-700', bgColor: 'bg-purple-50' },
    'Senior Collector': { icon: '👔', color: 'text-orange-700', bgColor: 'bg-orange-50' },
    'Financial Advisor': { icon: '💰', color: 'text-yellow-700', bgColor: 'bg-yellow-50' },
  };

  const runDebate = async (rounds: number = 2) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/multi-agent/debate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          context: caseData || {},
          debate_rounds: rounds,
        }),
      });

      const data = await response.json();
      setDebateResult(data);
    } catch (error) {
      console.error('Debate error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.85) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-orange-600';
  };

  const getConfidenceBgColor = (confidence: number) => {
    if (confidence >= 0.85) return 'bg-green-500';
    if (confidence >= 0.7) return 'bg-yellow-500';
    return 'bg-orange-500';
  };

  if (!debateResult) {
    return (
      <Card className="p-6">
        <div className="text-center space-y-4">
          <Brain className="w-16 h-16 mx-auto text-blue-600" />
          <h3 className="text-xl font-semibold">AI Strategy Debate</h3>
          <p className="text-gray-600">
            Let multiple AI agents debate the optimal collection strategy for this case.
          </p>
          {caseData && (
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-left">
              <div className="font-medium mb-2">Case Summary:</div>
              <div className="space-y-1 text-gray-700">
                <div>Amount: HK${caseData.overdue_amount.toLocaleString()}</div>
                <div>Days Overdue: {caseData.overdue_days}</div>
                <div>Status: {caseData.status}</div>
                {caseData.priority && <div>Priority: {caseData.priority}/10</div>}
              </div>
            </div>
          )}
          <Button
            onClick={() => runDebate(2)}
            disabled={isLoading}
            className="w-full bg-blue-600 hover:bg-blue-700"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                Running Debate...
              </span>
            ) : (
              'Run AI Strategy Debate'
            )}
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Consensus Recommendation */}
      <Card className="p-6 border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-blue-600" />
            <h3 className="text-xl font-semibold">Consensus Recommendation</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Confidence:</span>
            <span
              className={`text-2xl font-bold ${getConfidenceColor(
                debateResult.confidence
              )}`}
            >
              {(debateResult.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all ${getConfidenceBgColor(
                debateResult.confidence
              )}`}
              style={{ width: `${debateResult.confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Strategy */}
        <div className="bg-white rounded-lg p-4 mb-4">
          <div className="prose prose-sm max-w-none">
            <div className="whitespace-pre-wrap">{debateResult.consensus.strategy}</div>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            <span>{debateResult.consensus.num_agents} agents participated</span>
          </div>
          <div className="flex items-center gap-1">
            <CheckCircle className="w-4 h-4" />
            <span>
              {(debateResult.consensus.agreement_level * 100).toFixed(0)}% agreement
            </span>
          </div>
          <div>
            {debateResult.debate_rounds} round{debateResult.debate_rounds > 1 ? 's' : ''}
          </div>
        </div>

        {/* Trust Gate */}
        {debateResult.trust_gate_evaluation && (
          <div className="mb-4">
            <TrustGateBadge evaluation={debateResult.trust_gate_evaluation} />
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={() => onAccept?.(debateResult.consensus)}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            Accept Recommendation
          </Button>
          <Button
            onClick={() => runDebate(debateResult.debate_rounds + 1)}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
            disabled={isLoading}
          >
            Run Another Round
          </Button>
          <Button
            onClick={onReject}
            variant="outline"
            className="flex-1"
          >
            Override
          </Button>
        </div>
      </Card>

      {/* Agent Proposals */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5" />
          Agent Proposals (Round 1)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {debateResult.proposals.map((proposal) => {
            const config = agentConfig[proposal.agent] || {
              icon: '🤖',
              color: 'text-gray-700',
              bgColor: 'bg-gray-50',
            };
            const isExpanded = expandedAgent === proposal.agent;

            return (
              <div
                key={proposal.agent}
                className={`border rounded-lg p-4 ${config.bgColor} transition-all hover:shadow-md cursor-pointer`}
                onClick={() =>
                  setExpandedAgent(isExpanded ? null : proposal.agent)
                }
              >
                <div className="flex items-start gap-2 mb-2">
                  <span className="text-2xl">{config.icon}</span>
                  <div className="flex-1">
                    <div className={`font-semibold ${config.color}`}>
                      {proposal.agent}
                    </div>
                    <div className="text-xs text-gray-600">{proposal.expertise}</div>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-400" />
                  )}
                </div>

                <div
                  className={`text-sm text-gray-700 ${
                    isExpanded ? '' : 'line-clamp-3'
                  }`}
                >
                  {proposal.proposal}
                </div>

                {isExpanded && (
                  <div className="mt-3 pt-3 border-t">
                    <button className="text-sm text-blue-600 hover:underline">
                      View Full Proposal
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Critiques (if available) */}
      {debateResult.critiques && debateResult.critiques.length > 0 && (
        <Card className="p-6">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowCritiques(!showCritiques)}
          >
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <AlertCircle className="w-5 h-5" />
              Agent Critiques (Round 2)
            </h3>
            {showCritiques ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>

          {showCritiques && (
            <div className="mt-4 space-y-3">
              {debateResult.critiques.map((critique, index) => {
                const criticConfig = agentConfig[critique.critic] || {
                  icon: '🤖',
                  color: 'text-gray-700',
                };
                const targetConfig = agentConfig[critique.proposal_agent] || {
                  icon: '🤖',
                  color: 'text-gray-700',
                };

                return (
                  <div
                    key={index}
                    className="bg-gray-50 border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span>{criticConfig.icon}</span>
                      <span className={`font-medium ${criticConfig.color}`}>
                        {critique.critic}
                      </span>
                      <span className="text-gray-500">on</span>
                      <span>{targetConfig.icon}</span>
                      <span className={`font-medium ${targetConfig.color}`}>
                        {critique.proposal_agent}'s
                      </span>
                      <span className="text-gray-500">proposal:</span>
                    </div>
                    <div className="text-sm text-gray-700 pl-8">
                      {critique.critique}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      )}

      {/* Metadata Footer */}
      <div className="text-sm text-gray-500 text-center">
        Debate completed at {new Date(debateResult.debated_at).toLocaleString()}
      </div>
    </div>
  );
};
