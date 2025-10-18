# Invoice & Payment Dashboard

Modern React/Next.js Dashboard for Invoice Tracking & Payment Matching

## Features

✅ **Invoice Statistics** - Overview of all invoices (total, open, paid, overdue)  
✅ **Payment Matching** - Real-time match rate with circular progress  
✅ **Unmatched Transactions** - List of all unmatched payments with auto-match button  
✅ **Recent Invoices** - Table view of latest invoices with status badges  
✅ **Real-time API** - Connected to Railway Production API  

## Tech Stack

- **Next.js 14** - React framework with server-side rendering
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern utility-first CSS
- **Axios** - HTTP client for API calls
- **Recharts** - Chart library for data visualization

## Installation

```bash
cd dashboard
npm install
```

## Configuration

Set API URL in `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://my-langgraph-agent-production.up.railway.app
```

Or it defaults to Railway Production URL.

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Production Build

```bash
npm run build
npm start
```

## API Endpoints Used

- `GET /status` - Health check
- `GET /api/payment/statistics` - Payment matching stats
- `GET /api/payment/unmatched` - List of unmatched transactions
- `POST /api/payment/auto-match` - Trigger auto-matching

## Components

### `InvoiceStats.tsx`
Displays invoice overview with total count, paid/open/overdue breakdowns, and financial summary.

### `PaymentStats.tsx`
Shows payment matching statistics with circular progress indicator for match rate.

### `UnmatchedTransactions.tsx`
Lists all unmatched bank transactions with auto-match functionality.

### `RecentInvoices.tsx`
Table view of recent invoices with status badges and OneDrive links.

## Screenshots

Dashboard shows:
- Invoice totals (8 total, 3 paid, 4 open, 1 overdue)
- Payment match rate (80% circular progress)
- Unmatched transactions list with amounts
- Recent invoices table with filters

## Deployment

Can be deployed to:
- **Vercel** (recommended for Next.js)
- **Railway**
- **Netlify**
- **Docker**

```bash
# Vercel
vercel deploy

# Docker
docker build -t invoice-dashboard .
docker run -p 3000:3000 invoice-dashboard
```

## Future Features

🔜 Invoice search & filtering  
🔜 Date range selectors  
🔜 Export to CSV/Excel  
🔜 Dark mode  
🔜 Mobile responsive improvements  
🔜 Real-time updates (WebSocket)  

---

© 2025 C&D Tech GmbH
