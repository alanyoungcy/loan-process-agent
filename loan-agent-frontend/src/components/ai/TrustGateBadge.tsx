import React, { useState } from 'react';
import { Shield, CheckCircle, AlertCircle, XCircle, Info } from 'lucide-react';
import { Badge } from '../ui/Badge';

interface TrustGateEvaluation {
  decision: 'auto_execute' | 'human_review' | 'escalate' | 'block';
  confidence: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  reasoning: string;
  risk_factors: string[];
  requires_review: boolean;
  evaluated_at: string;
}

interface TrustGateBadgeProps {
  evaluation: TrustGateEvaluation;
  showDetails?: boolean;
  size?: 'sm' | 'md' | 'lg';
  onViewDetails?: () => void;
}

export const TrustGateBadge: React.FC<TrustGateBadgeProps> = ({
  evaluation,
  showDetails = false,
  size = 'md',
  onViewDetails,
}) => {
  const [expanded, setExpanded] = useState(showDetails);

  const getDecisionConfig = (decision: string) => {
    const configs: Record<
      string,
      {
        label: string;
        icon: React.ReactNode;
        color: string;
        bgColor: string;
        borderColor: string;
      }
    > = {
      auto_execute: {
        label: 'Auto-Execute',
        icon: <CheckCircle className="w-4 h-4" />,
        color: 'text-green-700',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
      },
      human_review: {
        label: 'Review Required',
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-yellow-700',
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
      },
      escalate: {
        label: 'Escalate',
        icon: <AlertCircle className="w-4 h-4" />,
        color: 'text-orange-700',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
      },
      block: {
        label: 'Blocked',
        icon: <XCircle className="w-4 h-4" />,
        color: 'text-red-700',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
      },
    };
    return configs[decision] || configs.human_review;
  };

  const getRiskLevelConfig = (riskLevel: string) => {
    const configs: Record<
      string,
      { label: string; emoji: string; color: string }
    > = {
      low: { label: 'Low Risk', emoji: '🟢', color: 'text-green-600' },
      medium: { label: 'Medium Risk', emoji: '🟡', color: 'text-yellow-600' },
      high: { label: 'High Risk', emoji: '🔴', color: 'text-orange-600' },
      critical: { label: 'Critical Risk', emoji: '⛔', color: 'text-red-600' },
    };
    return configs[riskLevel] || configs.medium;
  };

  const decisionConfig = getDecisionConfig(evaluation.decision);
  const riskConfig = getRiskLevelConfig(evaluation.risk_level);

  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  };

  return (
    <div className={`${sizeClasses[size]}`}>
      {/* Compact Badge View */}
      <div
        className={`inline-flex items-center gap-2 px-3 py-2 rounded-lg border ${decisionConfig.bgColor} ${decisionConfig.borderColor} ${decisionConfig.color} cursor-pointer hover:shadow-md transition-shadow`}
        onClick={() => setExpanded(!expanded)}
      >
        <Shield className="w-4 h-4" />
        <span className="font-medium">Trust Gate</span>
        <div className="flex items-center gap-1">
          {decisionConfig.icon}
          <span>{decisionConfig.label}</span>
        </div>
        {onViewDetails && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails();
            }}
            className="ml-2 hover:underline"
          >
            <Info className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div
          className={`mt-2 p-4 rounded-lg border ${decisionConfig.bgColor} ${decisionConfig.borderColor}`}
        >
          <div className="space-y-3">
            {/* Decision & Risk Level */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-semibold">Decision:</span>
                <div className="flex items-center gap-1">
                  {decisionConfig.icon}
                  <span className={decisionConfig.color}>{decisionConfig.label}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span>{riskConfig.emoji}</span>
                <span className={`font-medium ${riskConfig.color}`}>
                  {riskConfig.label}
                </span>
              </div>
            </div>

            {/* Confidence Score */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold">Confidence:</span>
                <span className="font-mono">{(evaluation.confidence * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    evaluation.confidence >= 0.8
                      ? 'bg-green-500'
                      : evaluation.confidence >= 0.6
                      ? 'bg-yellow-500'
                      : 'bg-orange-500'
                  }`}
                  style={{ width: `${evaluation.confidence * 100}%` }}
                />
              </div>
            </div>

            {/* Reasoning */}
            <div>
              <span className="font-semibold block mb-1">Reasoning:</span>
              <p className="text-gray-700">{evaluation.reasoning}</p>
            </div>

            {/* Risk Factors */}
            {evaluation.risk_factors && evaluation.risk_factors.length > 0 && (
              <div>
                <span className="font-semibold block mb-2">Risk Factors:</span>
                <ul className="space-y-1">
                  {evaluation.risk_factors.map((factor, index) => (
                    <li key={index} className="flex items-start gap-2 text-gray-700">
                      <span className="text-orange-500 mt-0.5">•</span>
                      <span>{factor}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Timestamp */}
            <div className="text-xs text-gray-500 pt-2 border-t">
              Evaluated at:{' '}
              {new Date(evaluation.evaluated_at).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface TrustGateStatusProps {
  evaluation: TrustGateEvaluation;
  actionType?: string;
  showPipeline?: boolean;
}

export const TrustGateStatus: React.FC<TrustGateStatusProps> = ({
  evaluation,
  actionType = 'Action',
  showPipeline = false,
}) => {
  const getStepStatus = (step: number) => {
    if (step === 1) return 'complete';
    if (step === 2) return evaluation.decision === 'block' ? 'failed' : 'complete';
    if (step === 3) {
      if (evaluation.decision === 'block') return 'blocked';
      if (evaluation.decision === 'auto_execute') return 'ready';
      return 'pending';
    }
    return 'pending';
  };

  const stepStatusConfig = {
    complete: { icon: <CheckCircle className="w-5 h-5" />, color: 'text-green-500' },
    failed: { icon: <XCircle className="w-5 h-5" />, color: 'text-red-500' },
    ready: { icon: <CheckCircle className="w-5 h-5" />, color: 'text-blue-500' },
    pending: { icon: <AlertCircle className="w-5 h-5" />, color: 'text-gray-400' },
    blocked: { icon: <XCircle className="w-5 h-5" />, color: 'text-red-500' },
  };

  if (!showPipeline) {
    return <TrustGateBadge evaluation={evaluation} />;
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-blue-600" />
        <h3 className="font-semibold text-gray-900">AI Action Pipeline</h3>
      </div>

      <div className="space-y-4">
        {/* Step 1: AI Generation */}
        <div className="flex items-start gap-3">
          <div className={stepStatusConfig[getStepStatus(1)].color}>
            {stepStatusConfig[getStepStatus(1)].icon}
          </div>
          <div className="flex-1">
            <div className="font-medium">1. AI Generation</div>
            <div className="text-sm text-gray-600">
              Generated {actionType.toLowerCase()}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Confidence: {(evaluation.confidence * 100).toFixed(0)}%
            </div>
          </div>
          <Badge color="green">Complete</Badge>
        </div>

        {/* Step 2: Trust Gate Review */}
        <div className="flex items-start gap-3">
          <div className={stepStatusConfig[getStepStatus(2)].color}>
            {stepStatusConfig[getStepStatus(2)].icon}
          </div>
          <div className="flex-1">
            <div className="font-medium">2. Trust Gate Review</div>
            <div className="text-sm text-gray-600">
              Decision: {evaluation.decision.replace('_', ' ')}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Risk: {evaluation.risk_level} | No violations
            </div>
          </div>
          <Badge
            color={
              evaluation.decision === 'block'
                ? 'red'
                : evaluation.decision === 'auto_execute'
                ? 'green'
                : 'yellow'
            }
          >
            {evaluation.decision === 'block' ? 'Failed' : 'Passed'}
          </Badge>
        </div>

        {/* Step 3: Execution */}
        <div className="flex items-start gap-3">
          <div className={stepStatusConfig[getStepStatus(3)].color}>
            {stepStatusConfig[getStepStatus(3)].icon}
          </div>
          <div className="flex-1">
            <div className="font-medium">3. Execution</div>
            <div className="text-sm text-gray-600">
              {evaluation.decision === 'auto_execute'
                ? 'Ready to execute'
                : evaluation.decision === 'block'
                ? 'Action blocked'
                : 'Awaiting human review'}
            </div>
          </div>
          <Badge
            color={
              evaluation.decision === 'auto_execute'
                ? 'blue'
                : evaluation.decision === 'block'
                ? 'red'
                : 'yellow'
            }
          >
            {evaluation.decision === 'auto_execute'
              ? 'Ready'
              : evaluation.decision === 'block'
              ? 'Blocked'
              : 'Pending'}
          </Badge>
        </div>
      </div>

      {/* Action Buttons */}
      {evaluation.requires_review && (
        <div className="mt-4 pt-4 border-t flex gap-2">
          <button className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium">
            Review Details
          </button>
          {evaluation.decision !== 'block' && (
            <button className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium">
              Approve & Execute
            </button>
          )}
        </div>
      )}

      {evaluation.decision === 'auto_execute' && !evaluation.requires_review && (
        <div className="mt-4 pt-4 border-t">
          <button className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium">
            Execute Now
          </button>
        </div>
      )}
    </div>
  );
};
