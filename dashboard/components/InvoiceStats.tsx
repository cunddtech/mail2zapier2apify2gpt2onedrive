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
    setLoading(true)
    
    // Mock data for now (API endpoint not yet created)
    // TODO: Replace with actual API call when invoice stats endpoint is ready
    
    const mockStats = {
      total_count: 8,
      open_count: 4,
      paid_count: 3,
      overdue_count: 1,
      open_incoming_total: 2234.55,
      open_outgoing_total: 2500.00,
      overdue_total: 999.99
    }
    
    setTimeout(() => {
      setStats(mockStats)
      setLoading(false)
    }, 500)
    
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
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-3xl font-bold text-blue-600">{stats?.total_count || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Gesamt</div>
        </div>
        
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-3xl font-bold text-green-600">{stats?.paid_count || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Bezahlt</div>
        </div>
        
        <div className="text-center p-4 bg-yellow-50 rounded-lg">
          <div className="text-3xl font-bold text-yellow-600">{stats?.open_count || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Offen</div>
        </div>
        
        <div className="text-center p-4 bg-red-50 rounded-lg">
          <div className="text-3xl font-bold text-red-600">{stats?.overdue_count || 0}</div>
          <div className="text-sm text-gray-600 mt-1">Überfällig</div>
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
