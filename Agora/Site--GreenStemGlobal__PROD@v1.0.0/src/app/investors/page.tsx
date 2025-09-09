import Hero from '@/components/Hero'
import { TrendingUp, Globe, Shield, Users } from 'lucide-react'

export const metadata = {
  title: 'For Investors',
  description: 'Invest in transparent agricultural supply chains connecting East Africa to EU markets.',
}

export default function InvestorsPage() {
  return (
    <>
      <Hero
        title="Transparent Supply Chains Win"
        subtitle="Building the infrastructure for traceable, compliant agricultural trade between East Africa and Europe."
        primaryCTA={{ text: 'Request Data Room', href: '/contact' }}
      />

      {/* Investment Thesis */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Investment Thesis</h2>
          <div className="max-w-4xl mx-auto">
            <div className="prose prose-lg text-gray-600">
              <p className="mb-6">
                The EU fresh produce market demands complete supply chain transparency, 
                driven by increasing regulatory requirements and consumer expectations. 
                GreenStemGlobal provides the operational infrastructure to meet these demands 
                while supporting East African farmers' access to premium markets.
              </p>
              <p className="mb-6">
                Our platform connects verified farms directly to EU buyers, eliminating 
                intermediaries while ensuring compliance with GlobalG.A.P., MRL standards, 
                and emerging carbon reporting requirements under CBAM.
              </p>
              <p>
                By investing in GreenStemGlobal, you support the development of sustainable 
                agricultural trade infrastructure that benefits all stakeholders in the value chain.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Use of Funds */}
      <section className="py-20 bg-light">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Use of Funds</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="card">
              <h3 className="font-semibold text-lg mb-3">Farm Inputs</h3>
              <p className="text-sm text-gray-600">
                Seeds, fertilizers, and pest management supplies for partner farmers
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-lg mb-3">Packhouse Upgrades</h3>
              <p className="text-sm text-gray-600">
                Cold storage facilities and processing equipment to maintain quality
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-lg mb-3">Certification</h3>
              <p className="text-sm text-gray-600">
                GlobalG.A.P. and organic certification costs for farmer groups
              </p>
            </div>
            <div className="card">
              <h3 className="font-semibold text-lg mb-3">Logistics SLAs</h3>
              <p className="text-sm text-gray-600">
                Guaranteed transport capacity and cold chain infrastructure
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Governance Structure */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Governance Structure</h2>
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-20 h-20 bg-leaf/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Globe className="h-10 w-10 text-leaf" />
                </div>
                <h3 className="font-semibold mb-2">German Entity</h3>
                <p className="text-sm text-gray-600">
                  EU market operations and buyer relationships
                </p>
              </div>
              <div className="text-center">
                <div className="w-20 h-20 bg-leaf/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Users className="h-10 w-10 text-leaf" />
                </div>
                <h3 className="font-semibold mb-2">Kenyan Entity</h3>
                <p className="text-sm text-gray-600">
                  Production management and farmer partnerships
                </p>
              </div>
              <div className="text-center">
                <div className="w-20 h-20 bg-leaf/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-10 w-10 text-leaf" />
                </div>
                <h3 className="font-semibold mb-2">US Entity</h3>
                <p className="text-sm text-gray-600">
                  Finance conduit and technology infrastructure
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Transparency */}
      <section className="py-20 bg-light">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Full Transparency</h2>
          <div className="max-w-3xl mx-auto">
            <div className="space-y-6">
              <div className="flex items-start">
                <TrendingUp className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Fund Flow Tracking</h3>
                  <p className="text-gray-600">
                    Each euro is tagged from wire transfer to farm payment to buyer delivery
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <TrendingUp className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Operational Metrics</h3>
                  <p className="text-gray-600">
                    Real-time dashboards showing volumes, quality metrics, and delivery performance
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <TrendingUp className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Impact Reporting</h3>
                  <p className="text-gray-600">
                    Quarterly reports on farmer income, training hours, and sustainability metrics
                  </p>
                </div>
              </div>
              <div className="flex items-start">
                <TrendingUp className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold mb-2">Compliance Documentation</h3>
                  <p className="text-gray-600">
                    All certifications, audit reports, and regulatory filings accessible via secure portal
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Market Opportunity */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Market Opportunity</h2>
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              <div className="card">
                <h3 className="font-semibold text-lg mb-3">EU Fresh Produce Demand</h3>
                <p className="text-gray-600 mb-4">
                  Growing demand for year-round fresh produce with full traceability
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Increasing regulatory requirements</li>
                  <li>• Consumer demand for transparency</li>
                  <li>• Shift towards direct sourcing</li>
                </ul>
              </div>
              <div className="card">
                <h3 className="font-semibold text-lg mb-3">East African Production</h3>
                <p className="text-gray-600 mb-4">
                  Ideal climate and growing conditions for EU market supply
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Year-round production capability</li>
                  <li>• Proximity to EU markets</li>
                  <li>• Experienced farming communities</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-stem text-white">
        <div className="container text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Join Us in Building Transparent Trade</h2>
          <p className="text-xl mb-8 text-gray-200 max-w-2xl mx-auto">
            Request access to our data room for detailed financial projections and operational metrics.
          </p>
          <a 
            href="/contact" 
            className="inline-block bg-white text-stem px-8 py-3 rounded-lg font-medium hover:bg-light transition-colors"
          >
            Request Data Room Access
          </a>
        </div>
      </section>
    </>
  )
}