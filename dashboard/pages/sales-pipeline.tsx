import SalesPipelineStats from '../components/SalesPipelineStats';
import RecentOpportunities from '../components/RecentOpportunities';

export default function SalesPipeline() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">💼 Sales Pipeline Dashboard</h1>
          <p className="text-gray-600">Überblick über alle Verkaufschancen und Pipeline-Status</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-1">
            <SalesPipelineStats />
          </div>
          <div className="lg:col-span-2">
            <RecentOpportunities />
          </div>
        </div>

        {/* Navigation Links */}
        <div className="mt-8 flex gap-4">
          <a 
            href="/" 
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Zurück zum Invoice Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
