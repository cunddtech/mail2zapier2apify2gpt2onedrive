import { useState, useEffect } from 'react'
import axios from 'axios'
import { formatDistance } from 'date-fns'
import { de } from 'date-fns/locale'

interface UnmatchedTransactionsProps {
  apiUrl: string
  refreshTrigger: number
}

interface Transaction {
  id: number
  transaction_id: string
  transaction_date: string
  amount: number
  sender_name: string
  receiver_name: string
  purpose: string
  reference: string
}

export default function UnmatchedTransactions({ apiUrl, refreshTrigger }: UnmatchedTransactionsProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    
    axios.get(`${apiUrl}/api/payment/unmatched`)
      .then(res => {
        setTransactions(res.data.transactions || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Unmatched transactions error:', err)
        setError('Fehler beim Laden')
        setLoading(false)
      })
  }, [apiUrl, refreshTrigger])

  const handleAutoMatch = async () => {
    try {
      await axios.post(`${apiUrl}/api/payment/auto-match`, {
        min_confidence: 0.7
      })
      
      // Refresh list
      const res = await axios.get(`${apiUrl}/api/payment/unmatched`)
      setTransactions(res.data.transactions || [])
      
      alert('Auto-Match erfolgreich ausgeführt!')
    } catch (err) {
      console.error('Auto-match error:', err)
      alert('Auto-Match fehlgeschlagen')
    }
  }

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          ⚠️ Unmatched Transactions
        </h2>
        
        <div className="flex items-center space-x-3">
          <span className="badge badge-warning">
            {transactions.length} offen
          </span>
          
          {transactions.length > 0 && (
            <button
              onClick={handleAutoMatch}
              className="btn btn-primary text-sm"
            >
              🔍 Auto-Match ausführen
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      {transactions.length === 0 ? (
        <div className="text-center py-12 bg-green-50 rounded-lg">
          <div className="text-4xl mb-2">✅</div>
          <p className="text-green-800 font-medium">
            Alle Transaktionen sind zugeordnet!
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {transactions.map((tx) => (
            <div
              key={tx.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:bg-blue-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className="badge badge-info text-xs">
                      ID: {tx.transaction_id}
                    </span>
                    <span className="text-sm text-gray-600">
                      {tx.transaction_date}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-700 mb-1">
                    <span className="font-medium">
                      {tx.amount > 0 ? tx.sender_name : tx.receiver_name}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600">
                    {tx.purpose?.substring(0, 80) || 'Kein Verwendungszweck'}
                    {tx.purpose && tx.purpose.length > 80 && '...'}
                  </div>
                </div>
                
                <div className="text-right ml-4">
                  <div className={`text-lg font-bold ${tx.amount > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {tx.amount.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                  </div>
                  <button className="btn btn-secondary text-xs mt-2">
                    Manuell zuordnen
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
