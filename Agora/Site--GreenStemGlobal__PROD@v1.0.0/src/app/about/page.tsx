import Hero from '@/components/Hero'
import { Award, Globe, Users, Target } from 'lucide-react'

export const metadata = {
  title: 'About Us',
  description: 'Learn about GreenStemGlobal and our mission to connect East African farmers with EU markets.',
}

export default function AboutPage() {
  return (
    <>
      <Hero
        title="Building Transparent Agricultural Trade"
        subtitle="Five years of pilots have led to an operational system connecting farms to markets."
      />

      {/* Our Story */}
      <section className="py-20 bg-white">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold mb-8">Our Story</h2>
            <div className="prose prose-lg text-gray-600 space-y-4">
              <p>
                GreenStemGlobal emerged from five years of intensive pilot programs 
                connecting East African smallholder farmers with European markets. 
                What started as an experiment in supply chain transparency has evolved 
                into a fully operational trading system.
              </p>
              <p>
                We recognized that the disconnect between high-quality East African 
                produce and EU market requirements wasn't about farming capability—it 
                was about infrastructure, certification, and traceability. Our platform 
                bridges these gaps with technology and operational excellence.
              </p>
              <p>
                Today, we work directly with farmer cooperatives in Kenya, Tanzania, 
                and Uganda, providing them with the tools, training, and market access 
                needed to thrive in international trade while maintaining sustainable 
                farming practices.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Standards & Certifications */}
      <section className="py-20 bg-light">
        <div className="container">
          <h2 className="text-3xl font-display font-bold text-center mb-12">Standards We Uphold</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="card text-center">
              <Award className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">GlobalG.A.P.</h3>
              <p className="text-sm text-gray-600">
                All partner farms maintain GlobalG.A.P. certification for Good Agricultural Practices
              </p>
            </div>
            <div className="card text-center">
              <Globe className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">ISO 14083</h3>
              <p className="text-sm text-gray-600">
                Carbon footprint quantification for transport services
              </p>
            </div>
            <div className="card text-center">
              <Target className="h-12 w-12 text-leaf mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">EU CBAM</h3>
              <p className="text-sm text-gray-600">
                Carbon Border Adjustment Mechanism reporting ready
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="py-20 bg-white">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-display font-bold text-center mb-12">Our Mission</h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-xl mb-4 text-stem">Farmer Empowerment</h3>
                <p className="text-gray-600">
                  We ensure farmers receive fair prices and invest in their capacity 
                  building. Training programs cover sustainable farming practices, 
                  quality management, and business skills.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-4 text-stem">Market Access</h3>
                <p className="text-gray-600">
                  By handling certification, logistics, and compliance, we open 
                  premium EU markets to smallholder farmers who would otherwise 
                  lack access to these opportunities.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-4 text-stem">Transparency</h3>
                <p className="text-gray-600">
                  Every transaction, shipment, and quality test is recorded and 
                  accessible. Buyers know exactly where their produce comes from 
                  and how it was grown.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-xl mb-4 text-stem">Sustainability</h3>
                <p className="text-gray-600">
                  We promote regenerative agriculture practices and help farmers 
                  adapt to climate change while reducing the carbon footprint of 
                  the supply chain.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="py-20 bg-light">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-display font-bold mb-8">Our Team</h2>
            <p className="text-lg text-gray-600 mb-8">
              GreenStemGlobal is led by a team with deep expertise in agricultural 
              supply chains, technology, and sustainable development.
            </p>
            <div className="card max-w-2xl mx-auto">
              <Users className="h-12 w-12 text-leaf mx-auto mb-4" />
              <p className="text-gray-600">
                Our team combines decades of experience in East African agriculture, 
                EU food import regulations, supply chain technology, and impact investing. 
                We work across three continents to ensure seamless operations from 
                farm to market.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-stem text-white">
        <div className="container text-center">
          <h2 className="text-3xl font-display font-bold mb-4">Join Our Mission</h2>
          <p className="text-xl mb-8 text-gray-200 max-w-2xl mx-auto">
            Whether you're a buyer, investor, or farmer, we'd love to hear from you.
          </p>
          <a 
            href="/contact" 
            className="inline-block bg-white text-stem px-8 py-3 rounded-lg font-medium hover:bg-light transition-colors"
          >
            Get in Touch
          </a>
        </div>
      </section>
    </>
  )
}
