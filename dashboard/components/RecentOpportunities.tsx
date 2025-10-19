import React, { useEffect, useState } from 'react';

interface Opportunity {
  id: number;
  title: string;
  stage: string;
  value: number | null;
  probability: number;
  contact_name: string | null;
  company_name: string | null;
  created_at: string;
  updated_at: string;
}

const RecentOpportunities: React.FC = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [stageFilter, setStageFilter] = useState<string>('all');

  useEffect(() => {
    fetchOpportunities();
  }, [stageFilter]);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const url = stageFilter === 'all' 
        ? 'https://my-langgraph-agent-production.up.railway.app/api/opportunity/recent?limit=20'
        : `https://my-langgraph-agent-production.up.railway.app/api/opportunity/recent?limit=20&stage=${stageFilter}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setOpportunities(data.opportunities);
      }
    } catch (err) {
      console.error('Error fetching opportunities:', err);
      // Fallback to mock data
      setOpportunities([
        {
          id: 1,
          title: 'Dachausbau - Mustermann GmbH',
          stage: 'proposal',
          value: 50000,
          probability: 60,
          contact_name: 'Max Mustermann',
          company_name: 'Mustermann GmbH',
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: 2,
          title: 'Anfrage Fassadensanierung',
          stage: 'lead',
          value: 75000,
          probability: 20,
          contact_name: 'Anna Schmidt',
          company_name: 'Schmidt Bau AG',
          created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 3,
          title: 'Preisanfrage Dachdeckerarbeiten',
          stage: 'qualified',
          value: 35000,
          probability: 40,
          contact_name: 'Peter Weber',
          company_name: null,
          created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | null) => {
    if (!value) return '—';
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: 'EUR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Heute';
    if (diffDays === 1) return 'Gestern';
    if (diffDays < 7) return `vor ${diffDays} Tagen`;
    
    return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  const getStageLabel = (stage: string) => {
    const labels: { [key: string]: string } = {
      lead: '🔵 Lead',
      qualified: '🟣 Qualifiziert',
      proposal: '🟡 Angebot',
      negotiation: '🟠 Verhandlung',
      won: '✅ Gewonnen',
      lost: '❌ Verloren'
    };
    return labels[stage] || stage;
  };

  const getStageColor = (stage: string) => {
    const colors: { [key: string]: string } = {
      lead: 'bg-blue-100 text-blue-800',
      qualified: 'bg-purple-100 text-purple-800',
      proposal: 'bg-yellow-100 text-yellow-800',
      negotiation: 'bg-orange-100 text-orange-800',
      won: 'bg-green-100 text-green-800',
      lost: 'bg-red-100 text-red-800'
    };
    return colors[stage] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Verkaufschancen</h2>
        <button 
          onClick={fetchOpportunities}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          🔄 Aktualisieren
        </button>
      </div>

      {/* Stage Filter */}
      <div className="flex gap-2 mb-4 overflow-x-auto">
        <button
          onClick={() => setStageFilter('all')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
            stageFilter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Alle
        </button>
        <button
          onClick={() => setStageFilter('lead')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
            stageFilter === 'lead' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🔵 Lead
        </button>
        <button
          onClick={() => setStageFilter('qualified')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
            stageFilter === 'qualified' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🟣 Qualifiziert
        </button>
        <button
          onClick={() => setStageFilter('proposal')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
            stageFilter === 'proposal' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🟡 Angebot
        </button>
        <button
          onClick={() => setStageFilter('negotiation')}
          className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
            stageFilter === 'negotiation' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          🟠 Verhandlung
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Lade Opportunities...</div>
      ) : opportunities.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          Keine Opportunities gefunden
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2 px-2 text-sm font-medium text-gray-600">Titel</th>
                <th className="text-left py-2 px-2 text-sm font-medium text-gray-600">Kontakt</th>
                <th className="text-center py-2 px-2 text-sm font-medium text-gray-600">Stage</th>
                <th className="text-right py-2 px-2 text-sm font-medium text-gray-600">Wert</th>
                <th className="text-center py-2 px-2 text-sm font-medium text-gray-600">%</th>
                <th className="text-right py-2 px-2 text-sm font-medium text-gray-600">Erstellt</th>
              </tr>
            </thead>
            <tbody>
              {opportunities.map((opp) => (
                <tr key={opp.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-2">
                    <div className="font-medium text-sm">{opp.title}</div>
                    {opp.company_name && (
                      <div className="text-xs text-gray-500">{opp.company_name}</div>
                    )}
                  </td>
                  <td className="py-3 px-2 text-sm">
                    {opp.contact_name || '—'}
                  </td>
                  <td className="py-3 px-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStageColor(opp.stage)}`}>
                      {getStageLabel(opp.stage)}
                    </span>
                  </td>
                  <td className="py-3 px-2 text-right font-medium text-sm">
                    {formatCurrency(opp.value)}
                  </td>
                  <td className="py-3 px-2 text-center text-sm">
                    <div className="flex items-center justify-center gap-1">
                      <div className="w-12 bg-gray-200 rounded-full h-1.5">
                        <div 
                          className="bg-blue-600 h-1.5 rounded-full"
                          style={{ width: `${opp.probability}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-600">{opp.probability}%</span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-right text-xs text-gray-500">
                    {formatDate(opp.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RecentOpportunities;
