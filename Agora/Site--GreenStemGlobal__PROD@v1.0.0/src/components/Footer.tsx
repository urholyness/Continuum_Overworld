import Link from 'next/link'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-soil text-white" role="contentinfo">
      <div className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company */}
          <div>
            <h3 className="text-lg font-display font-semibold mb-4">GreenStemGlobal</h3>
            <p className="text-gray-300 text-sm">
              Connecting EU buyers to verified East African farms with real-time traceability.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/buyers" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  For Buyers
                </Link>
              </li>
              <li>
                <Link href="/investors" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  For Investors
                </Link>
              </li>
              <li>
                <Link href="/trace" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  Traceability
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Compliance */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Standards</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>GlobalG.A.P. Certified</li>
              <li>ISO 14083 Compliant</li>
              <li>EU CBAM Ready</li>
              <li>MRL Compliance</li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/legal/imprint" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  Imprint
                </Link>
              </li>
              <li>
                <Link href="/legal/privacy" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-300 hover:text-leaf transition-colors text-sm">
                  Contact
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-700">
          <p className="text-center text-sm text-gray-300">
            © {currentYear} GreenStemGlobal. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
