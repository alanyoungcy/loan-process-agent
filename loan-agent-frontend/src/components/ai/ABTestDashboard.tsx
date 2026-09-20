import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Flask, TrendingUp, Play, StopCircle, Download, Calendar } from 'lucide-react';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface Experiment {
  name: string;
  description: string;
  status: 'active' | 'completed' | 'draft';
  start_date: string;
  end_date?: string;
  target_metric: string;
  target_sample_size: number;
  control: {
    total: number;
    successes: number;
    conversion_rate: number;
    confidence_interval: [number, number];
  };
  treatment: {
    total: number;
    successes: number;
    conversion_rate: number;
    confidence_interval: [number, number];
  };
  statistics: {
    lift_percentage: number;
    p_value: number | null;
    is_significant: boolean;
    winner: 'control' | 'treatment' | 'inconclusive' | 'insufficient_data';
  };
  sample_size_reached: boolean;
  control_description: string;
  treatment_description: string;
  hypothesis: string;
}

interface ABTestDashboardProps {
  onCreateExperiment?: () => void;
}

export const ABTestDashboard: React.FC<ABTestDashboardProps> = ({ onCreateExperiment }) => {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExperiment, setSelectedExperiment] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchExperiments();
  }, []);

  const fetchExperiments = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/experiments');
      const data = await response.json();
      setExperiments(data);
    } catch (error) {
      console.error('Failed to fetch experiments:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const stopExperiment = async (name: string) => {
    try {
      await fetch(`/api/v1/experiments/${name}/stop`, {
        method: 'POST',
      });
      fetchExperiments();
    } catch (error) {
      console.error('Failed to stop experiment:', error);
    }
  };

  const promoteWinner = async (name: string) => {
    try {
      await fetch(`/api/v1/experiments/${name}/promote`, {
        method: 'POST',
      });
      alert('Winner promoted successfully!');
      fetchExperiments();
    } catch (error) {
      console.error('Failed to promote winner:', error);
    }
  };

  const activeExperiments = experiments.filter((e) => e.status === 'active');
  const completedExperiments = experiments.filter((e) => e.status === 'completed');

  const getStatusColor = (status: string) => {
    return status === 'active' ? 'green' : status === 'completed' ? 'blue' : 'gray';
  };

  const getWinnerBadge = (winner: string) => {
    if (winner === 'treatment') return <Badge color="green">Treatment Wins</Badge>;
    if (winner === 'control') return <Badge color="blue">Control Wins</Badge>;
    if (winner === 'inconclusive') return <Badge color="yellow">Inconclusive</Badge>;
    return <Badge color="gray">Insufficient Data</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Flask className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold">A/B Testing Experiments</h1>
            <p className="text-gray-600">Optimize collection strategies with data</p>
          </div>
        </div>
        <Button
          onClick={onCreateExperiment}
          className="bg-blue-600 hover:bg-blue-700"
        >
          Create Experiment
        </Button>
      </div>

      {/* Active Experiments */}
      <div>
        <h2 className="text-xl font-semibold mb-4">
          Active Experiments ({activeExperiments.length})
        </h2>
        <div className="space-y-4">
          {activeExperiments.map((experiment) => (
            <ExperimentCard
              key={experiment.name}
              experiment={experiment}
              onStop={() => stopExperiment(experiment.name)}
              onView={() => setSelectedExperiment(experiment.name)}
            />
          ))}
          {activeExperiments.length === 0 && (
            <Card className="p-8 text-center text-gray-500">
              No active experiments. Create one to get started!
            </Card>
          )}
        </div>
      </div>

      {/* Completed Experiments */}
      {completedExperiments.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">
            Completed Experiments ({completedExperiments.length})
          </h2>
          <div className="space-y-4">
            {completedExperiments.slice(0, 3).map((experiment) => (
              <ExperimentCard
                key={experiment.name}
                experiment={experiment}
                onPromote={
                  experiment.statistics.is_significant &&
                  experiment.statistics.winner === 'treatment'
                    ? () => promoteWinner(experiment.name)
                    : undefined
                }
                onView={() => setSelectedExperiment(experiment.name)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

interface ExperimentCardProps {
  experiment: Experiment;
  onStop?: () => void;
  onPromote?: () => void;
  onView?: () => void;
}

const ExperimentCard: React.FC<ExperimentCardProps> = ({
  experiment,
  onStop,
  onPromote,
  onView,
}) => {
  const progress =
    ((experiment.control.total + experiment.treatment.total) /
      (experiment.target_sample_size * 2)) *
    100;

  const daysSinceStart = Math.floor(
    (Date.now() - new Date(experiment.start_date).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold">{experiment.name}</h3>
            <Badge color={experiment.status === 'active' ? 'green' : 'blue'}>
              {experiment.status === 'active' ? '🟢 Active' : '🔵 Completed'}
            </Badge>
          </div>
          <p className="text-gray-600 text-sm mb-2">{experiment.description}</p>
          <p className="text-gray-500 text-xs">
            <strong>Hypothesis:</strong> {experiment.hypothesis}
          </p>
        </div>
        <div className="flex gap-2">
          {onView && (
            <Button variant="outline" size="sm" onClick={onView}>
              View
            </Button>
          )}
          {onStop && (
            <Button variant="outline" size="sm" onClick={onStop}>
              <StopCircle className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="font-medium">Progress</span>
          <span className="text-gray-600">
            {experiment.control.total + experiment.treatment.total}/
            {experiment.target_sample_size * 2} samples
            {experiment.sample_size_reached && ' ✓'}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              experiment.sample_size_reached ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${Math.min(progress, 100)}%` }}
          />
        </div>
      </div>

      {/* Variants Comparison */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Control */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-2">Control</div>
          <div className="text-2xl font-bold text-gray-900 mb-1">
            {(experiment.control.conversion_rate * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            <div>N = {experiment.control.total}</div>
            <div>Successes = {experiment.control.successes}</div>
            <div className="text-xs text-gray-500">
              CI: [{(experiment.control.confidence_interval[0] * 100).toFixed(1)}%,{' '}
              {(experiment.control.confidence_interval[1] * 100).toFixed(1)}%]
            </div>
          </div>
        </div>

        {/* Treatment */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm font-medium text-blue-700 mb-2">Treatment</div>
          <div className="text-2xl font-bold text-blue-900 mb-1">
            {(experiment.treatment.conversion_rate * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-600 space-y-1">
            <div>N = {experiment.treatment.total}</div>
            <div>Successes = {experiment.treatment.successes}</div>
            <div className="text-xs text-gray-500">
              CI: [{(experiment.treatment.confidence_interval[0] * 100).toFixed(1)}%,{' '}
              {(experiment.treatment.confidence_interval[1] * 100).toFixed(1)}%]
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
        <div className="flex items-center gap-4">
          <div className="text-center">
            <div className="text-xs text-gray-600">Lift</div>
            <div
              className={`text-lg font-bold ${
                experiment.statistics.lift_percentage > 0
                  ? 'text-green-600'
                  : experiment.statistics.lift_percentage < 0
                  ? 'text-red-600'
                  : 'text-gray-600'
              }`}
            >
              {experiment.statistics.lift_percentage > 0 ? '+' : ''}
              {experiment.statistics.lift_percentage.toFixed(1)}%
            </div>
          </div>
          <div className="h-8 w-px bg-gray-300" />
          <div className="text-center">
            <div className="text-xs text-gray-600">p-value</div>
            <div className="text-lg font-bold text-gray-900">
              {experiment.statistics.p_value !== null
                ? experiment.statistics.p_value.toFixed(3)
                : 'N/A'}
            </div>
          </div>
          <div className="h-8 w-px bg-gray-300" />
          <div className="text-center">
            <div className="text-xs text-gray-600">Significance</div>
            <div className="text-lg">
              {experiment.statistics.is_significant ? '✅ Yes' : '⏳ Not Yet'}
            </div>
          </div>
        </div>
        <div>
          {experiment.statistics.winner === 'treatment' &&
          experiment.statistics.is_significant ? (
            <Badge color="green">Treatment Wins</Badge>
          ) : experiment.statistics.winner === 'control' &&
            experiment.statistics.is_significant ? (
            <Badge color="blue">Control Wins</Badge>
          ) : experiment.statistics.winner === 'inconclusive' ? (
            <Badge color="yellow">Inconclusive</Badge>
          ) : (
            <Badge color="gray">Continue Test</Badge>
          )}
        </div>
      </div>

      {/* Actions */}
      {experiment.status === 'active' && (
        <div className="mt-4 text-sm text-gray-600">
          Started {daysSinceStart} day{daysSinceStart !== 1 ? 's' : ''} ago
          {!experiment.sample_size_reached &&
            ` • Need ~${
              experiment.target_sample_size * 2 -
              (experiment.control.total + experiment.treatment.total)
            } more samples`}
        </div>
      )}

      {onPromote && experiment.statistics.is_significant && (
        <div className="mt-4 flex gap-2">
          <Button onClick={onPromote} className="flex-1 bg-green-600 hover:bg-green-700">
            Promote Winner
          </Button>
          <Button variant="outline" className="flex-1">
            Archive
          </Button>
        </div>
      )}
    </Card>
  );
};

interface CreateExperimentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (experiment: any) => void;
}

export const CreateExperimentModal: React.FC<CreateExperimentModalProps> = ({
  isOpen,
  onClose,
  onCreate,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    hypothesis: '',
    control_description: '',
    treatment_description: '',
    target_metric: 'payment_rate',
    target_sample_size: 500,
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/v1/experiments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await response.json();
      onCreate(data);
      onClose();
    } catch (error) {
      console.error('Failed to create experiment:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Create New A/B Test Experiment</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div>
              <h3 className="font-semibold mb-3">Basic Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Experiment Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Description *</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Hypothesis *</label>
                  <textarea
                    value={formData.hypothesis}
                    onChange={(e) =>
                      setFormData({ ...formData, hypothesis: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    rows={2}
                    required
                  />
                </div>
              </div>
            </div>

            {/* Variants */}
            <div>
              <h3 className="font-semibold mb-3">Variants</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Control (Baseline) *
                  </label>
                  <input
                    type="text"
                    value={formData.control_description}
                    onChange={(e) =>
                      setFormData({ ...formData, control_description: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Current email template"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Treatment (New Approach) *
                  </label>
                  <input
                    type="text"
                    value={formData.treatment_description}
                    onChange={(e) =>
                      setFormData({ ...formData, treatment_description: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Empathetic email template"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Metrics & Goals */}
            <div>
              <h3 className="font-semibold mb-3">Metrics & Goals</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">
                    Target Metric *
                  </label>
                  <select
                    value={formData.target_metric}
                    onChange={(e) =>
                      setFormData({ ...formData, target_metric: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="payment_rate">Payment Rate</option>
                    <option value="contact_success">Contact Success</option>
                    <option value="response_rate">Response Rate</option>
                    <option value="promise_to_pay">Promise to Pay</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">
                    Sample Size Per Variant *
                  </label>
                  <input
                    type="number"
                    value={formData.target_sample_size}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        target_sample_size: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    min="50"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Recommended: 500 for 80% power, 20% effect size
                  </p>
                </div>
              </div>
            </div>

            {/* Timeline */}
            <div>
              <h3 className="font-semibold mb-3">Timeline</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Start Date *</label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) =>
                      setFormData({ ...formData, start_date: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">
                    End Date (optional)
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) =>
                      setFormData({ ...formData, end_date: e.target.value })
                    }
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4 border-t">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                Cancel
              </Button>
              <Button type="submit" className="flex-1 bg-blue-600 hover:bg-blue-700">
                Create Experiment
              </Button>
            </div>
          </form>
        </div>
      </Card>
    </div>
  );
};
