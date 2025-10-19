import React, { useEffect, useState } from 'react';

interface PipelineStage {
  count: number;
  total_value: number;
  avg_probability: number;
}

interface PipelineStatistics {
  stages: {
    lead?: PipelineStage;
    qualified?: PipelineStage;
    proposal?: PipelineStage;
    negotiation?: PipelineStage;
  };
  won_lost: {
    won?: { count: number; total_value: number };
    lost?: { count: number; total_value: number };
  };
  weighted_pipeline_value: number;
}

const SalesPipelineStats: React.FC = () => {
  const [stats, setStats] = useState<PipelineStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://my-langgraph-agent-production.up.railway.app/api/opportunity/statistics');
      const data = await response.json();
      
      if (data.status === 'success') {
        setStats(data.statistics);
      } else {
        setError('Failed to load statistics');
      }
    } catch (err) {
      console.error('Error fetching pipeline stats:', err);
      // Fallback to mock data for development
      setStats({
        stages: {
          lead: { count: 5, total_value: 75000, avg_probability: 20 },
          qualified: { count: 3, total_value: 150000, avg_probability: 40 },
          proposal: { count: 2, total_value: 200000, avg_probability: 60 },
          negotiation: { count: 1, total_value: 100000, avg_probability: 80 }
        },
        won_lost: {
          won: { count: 8, total_value: 450000 },
          lost: { count: 3, total_value: 120000 }
        },
        weighted_pipeline_value: 267000
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const getStageLabel = (stage: string) => {
    const labels: { [key: string]: string } = {
      lead: 'Lead',
      qualified: 'Qualifiziert',
      proposal: 'Angebot',
      negotiation: 'Verhandlung'
    };
    return labels[stage] || stage;
  };

  const getStageColor = (stage: string) => {
    const colors: { [key: string]: string } = {
      lead: 'bg-blue-500',
      qualified: 'bg-purple-500',
      proposal: 'bg-yellow-500',
      negotiation: 'bg-orange-500'
    };
    return colors[stage] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Sales Pipeline</h2>
        <div className="text-center py-8 text-gray-500">Lade Daten...</div>
      </div>
    );
  }

  if (!stats) return null;

  const totalOpportunities = Object.values(stats.stages).reduce((sum, stage) => sum + (stage?.count || 0), 0);
  const totalValue = Object.values(stats.stages).reduce((sum, stage) => sum + (stage?.total_value || 0), 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">💼 Sales Pipeline</h2>
        <button 
          onClick={fetchStats}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          🔄 Aktualisieren
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Opportunities</div>
          <div className="text-2xl font-bold text-blue-900">{totalOpportunities}</div>
          <div className="text-xs text-gray-500 mt-1">aktive Verkaufschancen</div>
        </div>
        
        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Pipeline Wert</div>
          <div className="text-2xl font-bold text-green-900">{formatCurrency(totalValue)}</div>
          <div className="text-xs text-gray-500 mt-1">Gesamt</div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
          <div className="text-sm text-gray-600 mb-1">Gewichtet</div>
          <div className="text-2xl font-bold text-purple-900">
            {formatCurrency(stats.weighted_pipeline_value)}
          </div>
          <div className="text-xs text-gray-500 mt-1">nach Wahrscheinlichkeit</div>
        </div>
      </div>

      {/* Pipeline Stages */}
      <div className="space-y-4 mb-6">
        <h3 className="font-semibold text-gray-700">Pipeline Phasen</h3>
        {Object.entries(stats.stages).map(([stage, data]) => {
          if (!data || data.count === 0) return null;
          
          const percentage = totalValue > 0 ? (data.total_value / totalValue) * 100 : 0;
          
          return (
            <div key={stage} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStageColor(stage)}`}></div>
                  <span className="font-medium">{getStageLabel(stage)}</span>
                  <span className="text-sm text-gray-500">({data.count})</span>
                </div>
                <div className="text-right">
                  <div className="font-semibold">{formatCurrency(data.total_value)}</div>
                  <div className="text-xs text-gray-500">{data.avg_probability.toFixed(0)}% Ø</div>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`${getStageColor(stage)} h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Won/Lost Summary */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-green-600 font-medium">✅ Gewonnen</span>
          </div>
          <div className="text-xl font-bold text-green-900">
            {stats.won_lost.won?.count || 0}
          </div>
          <div className="text-sm text-gray-600">
            {formatCurrency(stats.won_lost.won?.total_value || 0)}
          </div>
        </div>
        
        <div className="bg-red-50 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-red-600 font-medium">❌ Verloren</span>
          </div>
          <div className="text-xl font-bold text-red-900">
            {stats.won_lost.lost?.count || 0}
          </div>
          <div className="text-sm text-gray-600">
            {formatCurrency(stats.won_lost.lost?.total_value || 0)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SalesPipelineStats;
