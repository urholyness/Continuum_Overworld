import type { Metadata } from 'next'
import './globals.css'
import NavBar from '@/components/NavBar'
import Footer from '@/components/Footer'

export const metadata: Metadata = {
  title: {
    default: 'GreenStemGlobal - Seed-to-Shelf Traceability',
    template: '%s | GreenStemGlobal'
  },
  description: 'Connecting EU buyers to verified East African farms with real-time traceability and compliance.',
  keywords: ['sustainable agriculture', 'traceability', 'East Africa', 'EU compliance', 'GlobalG.A.P.', 'supply chain'],
  authors: [{ name: 'GreenStemGlobal' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://greenstemglobal.com',
    siteName: 'GreenStemGlobal',
    title: 'GreenStemGlobal - Seed-to-Shelf Traceability',
    description: 'Connecting EU buyers to verified East African farms with real-time traceability and compliance.',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'GreenStemGlobal',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GreenStemGlobal - Seed-to-Shelf Traceability',
    description: 'Connecting EU buyers to verified East African farms with real-time traceability and compliance.',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <NavBar />
        <main id="main-content" className="flex-grow">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  )
}