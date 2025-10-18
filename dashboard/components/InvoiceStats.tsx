import { useState, useEffect } from 'react'
import axios from 'axios'

interface InvoiceStatsProps {
  apiUrl: string
  refreshTrigger: number
}

export default function InvoiceStats({ apiUrl, refreshTrigger }: InvoiceStatsProps) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true)
      
      try {
        // Try real API first
        const response = await axios.get(`${apiUrl}/api/invoice/statistics`)
        setStats(response.data.statistics)
      } catch (error) {
        console.log('Using mock data (API not ready):', error)
        
        // Fallback to mock data
        const mockStats = {
          total_count: 8,
          open_count: 4,
          paid_count: 3,
          overdue_count: 1,
          total_open_incoming: 2234.55,
          total_open_outgoing: 2500.00,
          total_overdue: 999.99
        }
        
        setStats(mockStats)
      } finally {
        setLoading(false)
      }
    }
    
    fetchStats()
  }, [apiUrl, refreshTrigger])

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-8 bg-gray-200 rounded"></div>
            <div className="h-8 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        📄 Rechnungen Übersicht
      </h2>

      {/* Summary Stats */}
            {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-3xl font-bold text-blue-600">{(stats?.total_count || stats?.count_open || 0) + (stats?.paid_count || 0)}</div>
          <div className="text-sm text-gray-600 mt-1">Gesamt</div>
        </div>
        
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-3xl font-bold text-green-600">{stats?.paid_count || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Bezahlt</div>
        </div>
        
        <div className="text-center p-4 bg-yellow-50 rounded-lg">
          <div className="text-3xl font-bold text-yellow-600">{stats?.open_count || stats?.count_open || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Offen</div>
        </div>
        
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <div className="text-3xl font-bold text-red-600">{stats?.overdue_count || stats?.count_overdue || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Überfällig</div>
        </div>
      </div>

      {/* Financial Summary */}
      <div className="border-t pt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Offen Eingehend:</span>
          <span className="font-semibold text-red-600">
            {(stats?.open_incoming_total || stats?.total_open_incoming || 0).toFixed(2)} EUR
          </span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Offen Ausgehend:</span>
          <span className="font-semibold text-green-600">
            {(stats?.open_outgoing_total || stats?.total_open_outgoing || 0).toFixed(2)} EUR
          </span>
        </div>
        
        <div className="flex justify-between text-sm font-bold border-t pt-2">
          <span className="text-gray-900">Überfällig:</span>
          <span className="text-red-600">
            {(stats?.overdue_total || stats?.total_overdue || 0).toFixed(2)} EUR
          </span>
        </div>
      </div>

      {/* Financial Summary */}
      <div className="space-y-3 border-t pt-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Offene Eingangsrechnungen:</span>
          <span className="text-lg font-semibold text-red-600">
            {stats?.open_incoming_total?.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) || '0,00 €'}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Offene Ausgangsrechnungen:</span>
          <span className="text-lg font-semibold text-green-600">
            {stats?.open_outgoing_total?.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) || '0,00 €'}
          </span>
        </div>
        
        {stats?.overdue_total > 0 && (
          <div className="flex justify-between items-center bg-red-50 p-3 rounded-lg">
            <span className="text-sm font-medium text-red-800">⚠️ Überfällig:</span>
            <span className="text-lg font-bold text-red-600">
              {stats.overdue_total.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
