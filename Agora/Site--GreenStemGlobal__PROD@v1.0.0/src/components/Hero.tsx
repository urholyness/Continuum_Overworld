import Link from 'next/link'

interface HeroProps {
  title: string
  subtitle: string
  primaryCTA?: {
    text: string
    href: string
  }
  secondaryCTA?: {
    text: string
    href: string
  }
}

export default function Hero({ title, subtitle, primaryCTA, secondaryCTA }: HeroProps) {
  return (
    <section className="bg-gradient-to-b from-light to-white py-20 md:py-32">
      <div className="container">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-display font-bold text-soil mb-6">
            {title}
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 mb-10">
            {subtitle}
          </p>
          
          {(primaryCTA || secondaryCTA) && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {primaryCTA && (
                <Link href={primaryCTA.href} className="btn-primary">
                  {primaryCTA.text}
                </Link>
              )}
              {secondaryCTA && (
                <Link href={secondaryCTA.href} className="btn-secondary">
                  {secondaryCTA.text}
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
