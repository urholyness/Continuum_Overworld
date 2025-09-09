import Hero from '@/components/Hero'
import Link from 'next/link'
import { Leaf, Globe, Shield, ArrowRight } from 'lucide-react'

export default function HomePage() {
  return (
    <>
      <Hero
        title="Seed-to-Shelf, Measured in Real Time."
        subtitle="GreenStemGlobal connects EU buyers to verified East African farms with traceability and compliance."
        primaryCTA={{ text: 'See Traceability', href: '/trace' }}
        secondaryCTA={{ text: 'Talk to Sales', href: '/buyers' }}
      />

      {/* Value Propositions */}
      <section className="py-20 bg-white">
        <div className="container">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card">
              <div className="flex items-center mb-4">
                <Globe className="h-8 w-8 text-leaf mr-3" />
                <h3 className="text-xl font-display font-semibold">Traceable by Design</h3>
              </div>
              <p className="text-gray-600">
                Field data and logistics events flow into buyer dashboards. Every step from farm to destination is recorded and verifiable.
              </p>
            </div>

            <div className="card">
              <div className="flex items-center mb-4">
                <Shield className="h-8 w-8 text-leaf mr-3" />
                <h3 className="text-xl font-display font-semibold">EU-Ready</h3>
              </div>
              <p className="text-gray-600">
                GlobalG.A.P. certified, residue compliance verified, and CBAM-prepared carbon reporting for seamless EU market access.
              </p>
            </div>

            <div className="card">
              <div className="flex items-center mb-4">
                <Leaf className="h-8 w-8 text-leaf mr-3" />
                <h3 className="text-xl font-display font-semibold">Farmer-Positive</h3>
              </div>
              <p className="text-gray-600">
                Profits reinvested into mechanization, training, and support for women-led farming households.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-20 bg-light">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Our Products</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">French Beans</h3>
              <p className="text-sm text-gray-600 mb-4">Extra fine, super fine, and fine grades available year-round</p>
              <Link href="/buyers" className="text-leaf font-medium flex items-center">
                Learn more <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Chili</h3>
              <p className="text-sm text-gray-600 mb-4">Cayenne varieties with consistent heat levels and color</p>
              <Link href="/buyers" className="text-leaf font-medium flex items-center">
                Learn more <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Passion Fruit</h3>
              <p className="text-sm text-gray-600 mb-4">Purple and yellow varieties with optimal brix levels</p>
              <Link href="/buyers" className="text-leaf font-medium flex items-center">
                Learn more <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>

            <div className="bg-white rounded-lg p-6 hover:shadow-lg transition-shadow">
              <h3 className="font-semibold text-lg mb-2">Macadamia</h3>
              <p className="text-sm text-gray-600 mb-4">Premium kernel grades with controlled moisture content</p>
              <Link href="/buyers" className="text-leaf font-medium flex items-center">
                Learn more <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">How We Work</h2>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-8">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 bg-leaf text-white rounded-full flex items-center justify-center font-semibold">
                  1
                </div>
                <div className="ml-4">
                  <h3 className="font-semibold text-lg mb-2">Pilot Shipment</h3>
                  <p className="text-gray-600">Start with a trial order to test quality, logistics, and documentation flow.</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 bg-leaf text-white rounded-full flex items-center justify-center font-semibold">
                  2
                </div>
                <div className="ml-4">
                  <h3 className="font-semibold text-lg mb-2">Steady Lane Development</h3>
                  <p className="text-gray-600">Build consistent supply lanes with regular shipments and quality monitoring.</p>
                </div>
              </div>

              <div className="flex items-start">
                <div className="flex-shrink-0 w-10 h-10 bg-leaf text-white rounded-full flex items-center justify-center font-semibold">
                  3
                </div>
                <div className="ml-4">
                  <h3 className="font-semibold text-lg mb-2">Annual Program</h3>
                  <p className="text-gray-600">Scale to annual contracts with dedicated farmer groups and guaranteed volumes.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-stem text-white">
        <div className="container text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-xl mb-8 text-gray-200">
            Connect with verified East African farms today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/contact" className="bg-white text-stem px-8 py-3 rounded-lg font-medium hover:bg-light transition-colors">
              Contact Sales
            </Link>
            <Link href="/trace" className="border-2 border-white text-white px-8 py-3 rounded-lg font-medium hover:bg-white hover:text-stem transition-colors">
              View Traceability
            </Link>
          </div>
        </div>
      </section>
    </>
  )
}