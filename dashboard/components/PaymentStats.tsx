import { useState, useEffect } from 'react'
import axios from 'axios'

interface PaymentStatsProps {
  apiUrl: string
  refreshTrigger: number
}

export default function PaymentStats({ apiUrl, refreshTrigger }: PaymentStatsProps) {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    
    axios.get(`${apiUrl}/api/payment/statistics`)
      .then(res => {
        setStats(res.data.statistics)
        setLoading(false)
      })
      .catch(err => {
        console.error('Payment stats error:', err)
        setError('Fehler beim Laden der Payment-Statistiken')
        setLoading(false)
      })
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

  if (error) {
    return (
      <div className="card bg-red-50">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

  const matchRate = stats?.match_rate || 0

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        💰 Payment Matching
      </h2>

      {/* Match Rate Circle */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative">
          <svg className="w-32 h-32 transform -rotate-90">
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke="#e5e7eb"
              strokeWidth="12"
              fill="none"
            />
            <circle
              cx="64"
              cy="64"
              r="56"
              stroke={matchRate >= 70 ? '#10b981' : matchRate >= 50 ? '#f59e0b' : '#ef4444'}
              strokeWidth="12"
              fill="none"
              strokeDasharray={`${2 * Math.PI * 56}`}
              strokeDashoffset={`${2 * Math.PI * 56 * (1 - matchRate / 100)}`}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900">{matchRate.toFixed(0)}%</div>
              <div className="text-xs text-gray-500">Match Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{stats?.total_transactions || 0}</div>
          <div className="text-xs text-gray-600 mt-1">Transaktionen</div>
        </div>
        
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{stats?.matched_count || 0}</div>
          <div className="text-xs text-gray-600 mt-1">Matched</div>
        </div>
      </div>

      {/* Unmatched & Amount */}
      <div className="space-y-3 border-t pt-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Unmatched:</span>
          <span className={`badge ${stats?.unmatched_count > 0 ? 'badge-warning' : 'badge-success'}`}>
            {stats?.unmatched_count || 0}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Matched Amount:</span>
          <span className="text-lg font-semibold text-green-600">
            {stats?.matched_amount?.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) || '0,00 €'}
          </span>
        </div>
      </div>
    </div>
  )
}
