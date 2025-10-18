import { useState, useEffect } from 'react'
import Head from 'next/head'
import axios from 'axios'
import { formatDistance } from 'date-fns'
import { de } from 'date-fns/locale'

import InvoiceStats from '../components/InvoiceStats'
import PaymentStats from '../components/PaymentStats'
import UnmatchedTransactions from '../components/UnmatchedTransactions'
import RecentInvoices from '../components/RecentInvoices'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://my-langgraph-agent-production.up.railway.app'

export default function Home() {
  const [loading, setLoading] = useState(true)
  const [apiStatus, setApiStatus] = useState<any>(null)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  useEffect(() => {
    // Check API status
    axios.get(`${API_URL}/status`)
      .then(res => {
        setApiStatus(res.data)
        setLoading(false)
      })
      .catch(err => {
        console.error('API not reachable:', err)
        setLoading(false)
      })
  }, [])

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Lade Dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Invoice & Payment Dashboard</title>
        <meta name="description" content="Invoice Tracking & Payment Matching Dashboard" />
      </Head>

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                📊 Invoice & Payment Dashboard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                C&D Tech GmbH • Rechnungsverwaltung & Zahlungsabgleich
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* API Status */}
              {apiStatus && (
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${apiStatus.status === 'ONLINE' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-600">
                    {apiStatus.status === 'ONLINE' ? 'API Online' : 'API Offline'}
                  </span>
                </div>
              )}
              
              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                className="btn btn-secondary text-sm"
              >
                🔄 Aktualisieren
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Top Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <InvoiceStats apiUrl={API_URL} refreshTrigger={refreshTrigger} />
          <PaymentStats apiUrl={API_URL} refreshTrigger={refreshTrigger} />
        </div>

        {/* Unmatched Transactions */}
        <div className="mb-8">
          <UnmatchedTransactions apiUrl={API_URL} refreshTrigger={refreshTrigger} />
        </div>

        {/* Recent Activity */}
        <div>
          <RecentInvoices apiUrl={API_URL} refreshTrigger={refreshTrigger} />
        </div>

      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © 2025 C&D Tech GmbH • Invoice & Payment Matching System v1.0
          </p>
        </div>
      </footer>
    </div>
  )
}
