import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Loan Collection System
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Post-Loan Collection Management with GenAI Integration
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Cases */}
          <Link href="/cases" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-4xl mb-4">📋</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Case Management
              </h2>
              <p className="text-gray-600">
                View and manage collection cases, assign to collectors
              </p>
            </div>
          </Link>

          {/* GenAI */}
          <Link href="/genai" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-4xl mb-4">🤖</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                AI Assistant
              </h2>
              <p className="text-gray-600">
                Generate summaries, scripts, and analyze customer intent with AI
              </p>
            </div>
          </Link>

          {/* Rules */}
          <Link href="/rules" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-4xl mb-4">⚖️</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Rules Engine
              </h2>
              <p className="text-gray-600">
                Configure Drools rules and decision tables
              </p>
            </div>
          </Link>

          {/* Analytics */}
          <Link href="/analytics" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-4xl mb-4">📊</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Analytics
              </h2>
              <p className="text-gray-600">
                View performance metrics and compliance reports
              </p>
            </div>
          </Link>

          {/* Compliance */}
          <Link href="/compliance" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer">
              <div className="text-4xl mb-4">🛡️</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Compliance Monitoring
              </h2>
              <p className="text-gray-600">
                Real-time monitoring of compliance violations and risks
              </p>
            </div>
          </Link>

          {/* Demo Data */}
          <Link href="/demo" className="block">
            <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer border-2 border-indigo-500">
              <div className="text-4xl mb-4">🎯</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                Demo Data
              </h2>
              <p className="text-gray-600">
                Generate demo data for presentations
              </p>
            </div>
          </Link>
        </div>

        {/* System Status */}
        <div className="mt-16 max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              System Status
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">●</div>
                <div className="text-sm text-gray-600 mt-2">Backend API</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">●</div>
                <div className="text-sm text-gray-600 mt-2">Database</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">●</div>
                <div className="text-sm text-gray-600 mt-2">Drools</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">●</div>
                <div className="text-sm text-gray-600 mt-2">RabbitMQ</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <div className="text-2xl font-bold text-indigo-600">0</div>
              <div className="text-sm text-gray-600 mt-1">Total Cases</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <div className="text-2xl font-bold text-green-600">0</div>
              <div className="text-sm text-gray-600 mt-1">Resolved</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <div className="text-2xl font-bold text-yellow-600">0</div>
              <div className="text-sm text-gray-600 mt-1">In Progress</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">0</div>
              <div className="text-sm text-gray-600 mt-1">AI Processed</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-gray-600">
          <p className="text-sm">
            Phase 0 & 1 Complete - Backend API Ready | Frontend UI Ready
          </p>
          <p className="text-xs mt-2">
            Powered by FastAPI, Next.js, Drools & GenAI
          </p>
        </div>
      </div>
    </div>
  );
}
