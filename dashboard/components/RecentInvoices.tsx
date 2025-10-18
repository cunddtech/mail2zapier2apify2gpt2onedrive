import { useState, useEffect } from 'react'
import axios from 'axios'

interface RecentInvoicesProps {
  apiUrl: string
  refreshTrigger: number
}

interface Invoice {
  id?: number
  invoice_number: string
  invoice_date: string
  due_date: string
  amount_total: number
  currency?: string
  vendor_name?: string
  customer_name?: string
  direction: string
  status: string
  onedrive_link?: string
  payment_date?: string
  created_at?: string
}

export default function RecentInvoices({ apiUrl, refreshTrigger }: RecentInvoicesProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchInvoices = async () => {
      setLoading(true)
      
      try {
        // Try real API first
        const response = await axios.get(`${apiUrl}/api/invoice/recent?limit=20`)
        setInvoices(response.data.invoices)
      } catch (error) {
        console.log('Using mock data (API not ready):', error)
        
        // Fallback to mock data
        const mockInvoices: Invoice[] = [
          {
            invoice_number: 'RE-2025-001',
            invoice_date: '2025-10-01',
            due_date: '2025-10-31',
            amount_total: 1234.56,
            vendor_name: 'Novoferm Vertriebs GmbH',
            customer_name: 'C&D Tech GmbH',
            direction: 'incoming',
            status: 'paid',
            onedrive_link: 'https://cdtech1-my.sharepoint.com/...'
          },
          {
            invoice_number: 'RE-2025-002',
            invoice_date: '2025-10-05',
            due_date: '2025-11-05',
            amount_total: 2500.00,
            vendor_name: 'Best Customer AG',
            customer_name: 'C&D Tech GmbH',
            direction: 'outgoing',
            status: 'paid'
          },
          {
            invoice_number: 'RE-2025-003',
            invoice_date: '2025-09-15',
            due_date: '2025-10-15',
            amount_total: 999.99,
            vendor_name: 'Supplier XYZ',
            customer_name: 'C&D Tech GmbH',
            direction: 'incoming',
            status: 'overdue'
          }
        ]
        
        setInvoices(mockInvoices)
      } finally {
        setLoading(false)
      }
    }
    
    fetchInvoices()
  }, [apiUrl, refreshTrigger])

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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return <span className="badge badge-success">Bezahlt</span>
      case 'open':
        return <span className="badge badge-info">Offen</span>
      case 'overdue':
        return <span className="badge badge-danger">Überfällig</span>
      default:
        return <span className="badge">{status}</span>
    }
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        📋 Aktuelle Rechnungen
      </h2>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rechnungsnr.
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Datum
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Partner
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Typ
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Betrag
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Aktionen
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {invoices.map((invoice, idx) => (
              <tr key={invoice.invoice_number || idx} className="hover:bg-gray-50">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-blue-600">
                  {invoice.invoice_number}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                  {invoice.invoice_date}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700">
                  {invoice.direction === 'incoming' ? (invoice.vendor_name || 'N/A') : (invoice.customer_name || 'N/A')}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  {invoice.direction === 'incoming' ? (
                    <span className="text-red-600">↓ Eingang</span>
                  ) : (
                    <span className="text-green-600">↑ Ausgang</span>
                  )}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-semibold text-right">
                  {invoice.amount_total.toLocaleString('de-DE', { style: 'currency', currency: 'EUR' })}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center">
                  {getStatusBadge(invoice.status)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-center text-sm">
                  {invoice.onedrive_link ? (
                    <a
                      href={invoice.onedrive_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800"
                    >
                      📄 Öffnen
                    </a>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {invoices.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Keine Rechnungen vorhanden
        </div>
      )}
    </div>
  )
}
