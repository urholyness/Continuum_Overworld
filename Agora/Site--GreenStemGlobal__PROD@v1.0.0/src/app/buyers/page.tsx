import Hero from '@/components/Hero'
import { CheckCircle, Package, Truck, FileCheck } from 'lucide-react'

export const metadata = {
  title: 'For Buyers',
  description: 'Access verified East African produce with full traceability and EU compliance.',
}

export default function BuyersPage() {
  return (
    <>
      <Hero
        title="Direct from Verified Farms"
        subtitle="Access premium East African produce with complete traceability and EU compliance."
        primaryCTA={{ text: 'Request Sample Shipment', href: '/contact' }}
      />

      {/* Products Section */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Product Specifications</h2>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* French Beans */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">French Beans</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Grades Available:</span>
                  <ul className="mt-1 ml-4 text-sm text-gray-600 list-disc">
                    <li>Extra Fine: 6-8mm diameter</li>
                    <li>Super Fine: 8-10mm diameter</li>
                    <li>Fine: 10-12mm diameter</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium">Packaging:</span>
                  <p className="text-sm text-gray-600">2kg, 4kg, 5kg cartons</p>
                </div>
                <div>
                  <span className="font-medium">Availability:</span>
                  <p className="text-sm text-gray-600">Year-round production</p>
                </div>
                <div>
                  <span className="font-medium">Certifications:</span>
                  <p className="text-sm text-gray-600">GlobalG.A.P., MRL compliant</p>
                </div>
              </div>
            </div>

            {/* Chili */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">Chili</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Varieties:</span>
                  <p className="text-sm text-gray-600">Cayenne (Long Slim)</p>
                </div>
                <div>
                  <span className="font-medium">Specifications:</span>
                  <ul className="mt-1 ml-4 text-sm text-gray-600 list-disc">
                    <li>Length: 10-15cm</li>
                    <li>Scoville: 30,000-50,000 SHU</li>
                    <li>Color: Bright red at maturity</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium">Packaging:</span>
                  <p className="text-sm text-gray-600">1kg, 2kg, 5kg cartons</p>
                </div>
                <div>
                  <span className="font-medium">Harvest Cycles:</span>
                  <p className="text-sm text-gray-600">Two main seasons plus off-season availability</p>
                </div>
              </div>
            </div>

            {/* Passion Fruit */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">Passion Fruit</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Varieties:</span>
                  <ul className="mt-1 ml-4 text-sm text-gray-600 list-disc">
                    <li>Purple passion fruit</li>
                    <li>Yellow passion fruit</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium">Size Grades:</span>
                  <p className="text-sm text-gray-600">Grade A: 50-70mm, Grade B: 40-50mm</p>
                </div>
                <div>
                  <span className="font-medium">Brix Level:</span>
                  <p className="text-sm text-gray-600">12-18° Brix at harvest</p>
                </div>
                <div>
                  <span className="font-medium">Season:</span>
                  <p className="text-sm text-gray-600">Peak: March-August, Available: Year-round</p>
                </div>
              </div>
            </div>

            {/* Macadamia */}
            <div className="card">
              <h3 className="text-xl font-semibold mb-4">Macadamia</h3>
              <div className="space-y-3">
                <div>
                  <span className="font-medium">Kernel Sizes:</span>
                  <ul className="mt-1 ml-4 text-sm text-gray-600 list-disc">
                    <li>Style 0: Whole kernel</li>
                    <li>Style 1: Halves</li>
                    <li>Style 2: Large pieces</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium">Moisture Content:</span>
                  <p className="text-sm text-gray-600">1.5% maximum</p>
                </div>
                <div>
                  <span className="font-medium">Packaging:</span>
                  <p className="text-sm text-gray-600">Vacuum-sealed 5kg, 11.34kg boxes</p>
                </div>
                <div>
                  <span className="font-medium">Harvest:</span>
                  <p className="text-sm text-gray-600">Main: February-June</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quality Assurance */}
      <section className="py-20 bg-light">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Quality Assurance</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <FileCheck className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Pre-Harvest Testing</h3>
              <p className="text-sm text-gray-600">
                MRL testing and certification before harvest begins
              </p>
            </div>
            <div className="text-center">
              <Package className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Packhouse Standards</h3>
              <p className="text-sm text-gray-600">
                Temperature-controlled facilities with HACCP protocols
              </p>
            </div>
            <div className="text-center">
              <Truck className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Cold Chain Integrity</h3>
              <p className="text-sm text-gray-600">
                Monitored transport from packhouse to destination
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Process */}
      <section className="py-20 bg-white">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Partnership Process</h2>
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-start">
              <CheckCircle className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">1. Initial Consultation</h3>
                <p className="text-gray-600">Discuss your requirements, volumes, and quality specifications</p>
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">2. Sample Shipment</h3>
                <p className="text-gray-600">Receive a pilot shipment to verify quality and logistics</p>
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">3. QA Portal Access</h3>
                <p className="text-gray-600">Get live access to quality data and shipment tracking</p>
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">4. Steady Lane Development</h3>
                <p className="text-gray-600">Build consistent supply with regular shipments</p>
              </div>
            </div>
            <div className="flex items-start">
              <CheckCircle className="h-6 w-6 text-leaf mr-3 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">5. Annual Program</h3>
                <p className="text-gray-600">Scale to annual contracts with dedicated farmer groups</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-stem text-white">
        <div className="container text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Ready to Source Direct?</h2>
          <p className="text-xl mb-8 text-gray-200 max-w-2xl mx-auto">
            Start with a sample shipment and experience our quality and traceability firsthand.
          </p>
          <a 
            href="/contact" 
            className="inline-block bg-white text-stem px-8 py-3 rounded-lg font-medium hover:bg-light transition-colors"
          >
            Request Sample Shipment
          </a>
        </div>
      </section>
    </>
  )
}