'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { motion, useInView } from 'framer-motion'
import { Leaf, Globe, Shield, ThermometerSun, Droplets, Sprout, Factory, CheckCircle2, Truck, Gauge, Recycle, Salad, FlameKindling, Grape, TreePine, Globe2 } from 'lucide-react'

function useCountUp(target: number, duration = 1500) {
  const [value, setValue] = useState(0)
  const started = useRef(false)
  const ref = useRef<HTMLDivElement | null>(null)
  const inView = useInView(ref, { margin: '0px 0px -20% 0px' })

  useEffect(() => {
    if (!inView || started.current) return
    started.current = true
    const t0 = performance.now()
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / duration)
      setValue(Math.floor(target * (1 - Math.pow(1 - p, 3))))
      if (p < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [inView, target, duration])
  
  return { ref, value } as const
}

const PhotoChip = ({ label, gradient }: { label: string; gradient: string }) => (
  <div className="group flex flex-col items-center">
    <div className={`h-20 w-20 rounded-full ${gradient} shadow-sm ring-1 ring-emerald-200/40`} />
    <span className="mt-2 text-xs text-slate-600 group-hover:text-slate-800">{label}</span>
  </div>
)

export default function HomePage() {
  const [farmData, setFarmData] = useState<any>(null)

  useEffect(() => {
    // For static export, we'll use mock data initially and enhance with real data later
    const mockFarmData = {
      farms: [
        {
          id: "GSG-KE-UG-001",
          name: "GSG-KE-UG Farm",
          location: "Eldoret, Kenya",
          coordinates: { lat: 0.5143, lng: 35.2698 },
          size: "9 acres",
          crop: "French Beans - Star 2008",
          ndvi: 0.71,
          temperature: 22,
          humidity: 58,
          harvest: 1200
        }
      ]
    }
    
    setFarmData(mockFarmData)

    // In production, this will try to fetch live data but won't break static build
    if (typeof window !== 'undefined') {
      const fetchLiveData = async () => {
        try {
          const response = await fetch('/api/trace/lots')
          if (response.ok) {
            const liveData = await response.json()
            setFarmData(liveData)
          }
        } catch (error) {
          console.log('Live data not available, using default data')
        }
      }

      setTimeout(fetchLiveData, 2000) // Delay to avoid blocking initial render
      const interval = setInterval(fetchLiveData, 30000)
      return () => clearInterval(interval)
    }
  }, [])

  return (
    <div className="min-h-screen w-full bg-[#F7FBF5] text-slate-800 selection:bg-emerald-200/60 selection:text-emerald-900 overflow-x-hidden relative">
      <PollenField />
      <FieldGrid />
      <GrowthField />
      
      <HeroSection />
      <DividerLeaf />
      <WhatWeDo />
      <LiveFarmIntelligence farmData={farmData} />
      <CropsAndSeasons />
      <HowItWorks />
      <ImpactAssurance />
      <FinalCTA />
      <DataStream />
    </div>
  )
}

function PollenField() {
  useEffect(() => {
    const particles = []
    const container = document.createElement('div')
    container.className = 'fixed inset-0 pointer-events-none z-[1]'
    document.body.appendChild(container)

    for (let i = 0; i < 40; i++) {
      const particle = document.createElement('div')
      particle.className = 'absolute w-1 h-1 bg-emerald-400 rounded-full opacity-0 blur-sm'
      particle.style.left = Math.random() * 100 + '%'
      particle.style.animationDelay = Math.random() * 25 + 's'
      particle.style.animation = `drift ${20 + Math.random() * 10}s infinite linear`
      container.appendChild(particle)
      particles.push(particle)
    }

    const style = document.createElement('style')
    style.textContent = `
      @keyframes drift {
        0% {
          transform: translate(0, 100vh) rotate(0deg);
          opacity: 0;
        }
        10% {
          opacity: 0.6;
        }
        90% {
          opacity: 0.6;
        }
        100% {
          transform: translate(100px, -100vh) rotate(360deg);
          opacity: 0;
        }
      }
    `
    document.head.appendChild(style)

    return () => {
      container.remove()
      style.remove()
    }
  }, [])

  return null
}

function FieldGrid() {
  return (
    <div className="fixed inset-0 z-0 opacity-30">
      <div 
        className="w-full h-full"
        style={{
          backgroundImage: `
            linear-gradient(rgba(16,185,129,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(16,185,129,0.02) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
          transform: 'perspective(500px) rotateX(15deg)',
          transformOrigin: 'center center'
        }}
      />
    </div>
  )
}

function GrowthField() {
  return (
    <div className="fixed inset-0 z-0">
      <div className="w-full h-full bg-gradient-to-b from-emerald-50/10 via-emerald-50/5 to-transparent" />
      <div className="absolute -top-24 -right-24 h-80 w-80 rounded-full bg-emerald-200/20 blur-3xl" />
      <div className="absolute -bottom-24 -left-24 h-80 w-80 rounded-full bg-lime-200/20 blur-3xl" />
    </div>
  )
}

function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center px-6 py-20 z-10">
      <div className="text-center max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
          className="inline-flex items-center gap-2 rounded-full bg-white/80 ring-1 ring-emerald-200 px-4 py-2 text-sm text-emerald-700 mb-6"
        >
          <Leaf className="h-4 w-4" />
          Sustainable farming • EU-grade quality • Real traceability
        </motion.div>
        
        <motion.h1
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 0.2, ease: 'easeOut' }}
          className="text-5xl sm:text-7xl lg:text-8xl font-black leading-tight tracking-tight mb-6"
        >
          <span className="block">Seed-to-Shelf,</span>
          <span className="block bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 via-green-500 to-lime-500">
            Measured in Real Time
          </span>
        </motion.h1>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 0.85, y: 0 }}
          transition={{ duration: 1.2, delay: 0.4, ease: 'easeOut' }}
          className="text-xl sm:text-2xl font-light mb-4 text-slate-700 max-w-4xl mx-auto leading-relaxed"
        >
          TRACEABLE BY DESIGN
        </motion.p>
        
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 0.75, y: 0 }}
          transition={{ duration: 1.2, delay: 0.6, ease: 'easeOut' }}
          className="text-lg mb-12 text-slate-700 max-w-3xl mx-auto leading-relaxed"
        >
          GreenStemGlobal connects EU buyers to verified East African farms with satellite intelligence. 
          Every harvest monitored from space, every grade verified, every shipment tracked to destination.
        </motion.p>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 0.8, ease: 'easeOut' }}
          className="flex flex-col sm:flex-row gap-6 justify-center mb-12"
        >
          <Link
            href="/trace"
            className="px-8 py-4 bg-gradient-to-r from-emerald-600 to-green-500 text-white rounded-xl font-semibold text-lg hover:from-emerald-500 hover:to-green-400 transition-all duration-300 hover:scale-105 hover:shadow-lg shadow-emerald-200"
          >
            See Live Traceability
          </Link>
          <Link
            href="/buyers"
            className="px-8 py-4 bg-white text-emerald-800 border-2 border-emerald-200 rounded-xl font-semibold text-lg hover:bg-emerald-50 transition-all duration-300 hover:scale-105"
          >
            Talk to Sales
          </Link>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 1, ease: 'easeOut' }}
          className="flex items-center justify-center gap-8"
        >
          <PhotoChip label="French Beans" gradient="bg-gradient-to-br from-emerald-300 to-emerald-500" />
          <PhotoChip label="Chili" gradient="bg-gradient-to-br from-orange-300 to-red-400" />
          <PhotoChip label="Passion Fruit" gradient="bg-gradient-to-br from-fuchsia-300 to-purple-400" />
          <PhotoChip label="Macadamia" gradient="bg-gradient-to-br from-amber-300 to-amber-500" />
        </motion.div>
      </div>
    </section>
  )
}

function DividerLeaf() {
  return (
    <div className="mx-auto max-w-7xl px-6 py-6">
      <div className="flex items-center gap-3 text-emerald-700/80">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent" />
        <Leaf className="h-4 w-4" />
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent" />
      </div>
    </div>
  )
}

function WhatWeDo() {
  const tiles = [
    { icon: <Sprout className="h-5 w-5" />, title: "We Grow", body: "Own and partner farms across Kenya with field protocols and crop rotation." },
    { icon: <Factory className="h-5 w-5" />, title: "We Pack & Aggregate", body: "Sorting, grading, and export prep in EU-aligned pack processes." },
    { icon: <CheckCircle2 className="h-5 w-5" />, title: "We Assure Quality", body: "Residue testing, GlobalG.A.P. pathway, and shipment QC lots." },
    { icon: <Truck className="h-5 w-5" />, title: "We Move Cold-Chain", body: "4-6°C handling, fast routes NBO → FRA/AMS, on-time coordination." },
    { icon: <Gauge className="h-5 w-5" />, title: "We Trace & Report", body: "Lot-level traceability with farm GPS, temp trail, and carbon estimate." },
    { icon: <Recycle className="h-5 w-5" />, title: "We Steward Impact", body: "Water-wise irrigation, soil health, and livelihoods for growers." },
  ]

  return (
    <section className="py-20 z-10 relative">
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">What we do</h2>
        <p className="text-xl text-slate-700 max-w-3xl mb-12">
          GreenStemGlobal is a sustainable farming company: production, aggregation, quality, logistics, and transparent data — on one clean rail.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {tiles.map((tile, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="bg-white/80 backdrop-blur border border-emerald-100 rounded-2xl p-6 hover:shadow-lg hover:scale-105 transition-all duration-300 hover:border-emerald-200"
            >
              <div className="flex items-center gap-3 text-emerald-700 mb-4">
                {tile.icon}
                <h3 className="text-lg font-semibold">{tile.title}</h3>
              </div>
              <p className="text-slate-700">{tile.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function LiveFarmIntelligence({ farmData }: { farmData: any }) {
  return (
    <section className="py-20 bg-gradient-to-b from-white to-emerald-50/30 z-10 relative">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-emerald-800 mb-4">Live Farm Intelligence</h2>
          <p className="text-lg text-slate-700">Real-time satellite monitoring of our verified farms</p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <FarmCard 
            title="GSG-KE-UG Farm" 
            location="Eldoret, Kenya"
            coordinates="0.5143°N, 35.2698°E"
            size="9 acres"
            crop="French Beans - Star 2008"
            ndvi="0.71"
            temp="22°C"
            humidity="58%"
            harvest="1,200 kg/week"
            farmData={farmData}
          />
          <FarmCard 
            title="GSG-KE-UG Extension" 
            location="Eldoret, Kenya"
            coordinates="0.5156°N, 35.2685°E"
            size="6 acres"
            crop="Chili - Cayenne"
            ndvi="0.68"
            temp="23°C"
            humidity="61%"
            harvest="800 kg/week"
            farmData={farmData}
          />
        </div>
      </div>
    </section>
  )
}

function FarmCard({ title, location, coordinates, size, crop, ndvi, temp, humidity, harvest, farmData }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-white/90 backdrop-blur border border-emerald-200 rounded-2xl p-6 hover:shadow-xl transition-all duration-500 hover:scale-105"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-emerald-800">{title}</h3>
        <div className="flex items-center gap-2 text-sm text-amber-600 font-semibold">
          <div className="w-3 h-3 bg-amber-400 rounded-full animate-pulse" />
          LIVE FEED
        </div>
      </div>
      
      <div className="aspect-[4/3] w-full rounded-xl bg-gradient-to-br from-emerald-100 to-lime-100 mb-4 relative overflow-hidden">
        <div className="absolute top-3 right-3 bg-black/80 backdrop-blur px-3 py-2 rounded-lg border border-emerald-200/30">
          <span className="text-xs text-white/70 mr-2">NDVI:</span>
          <span className="text-sm font-bold text-emerald-400">{ndvi}</span>
        </div>
        <SatelliteView ndvi={parseFloat(ndvi)} />
      </div>
      
      <div className="grid grid-cols-2 gap-3 text-sm">
        <DataPoint label="Location" value={location} />
        <DataPoint label="Size" value={size} />
        <DataPoint label="Crop" value={crop} />
        <DataPoint label="GPS" value={coordinates} />
        <DataPoint label="Temperature" value={temp} />
        <DataPoint label="Humidity" value={humidity} />
        <DataPoint label="Harvest" value={harvest} />
        <DataPoint label="Owner" value="GSG-KE-UG" />
      </div>
      
      <div className="mt-4 flex items-center gap-4 text-xs text-emerald-700">
        <div className="flex items-center gap-2">
          <ThermometerSun className="h-4 w-4" />
          <span>4-6°C cold-chain</span>
        </div>
        <div className="flex items-center gap-2">
          <Droplets className="h-4 w-4" />
          <span>EU residue compliant</span>
        </div>
        <div className="flex items-center gap-2">
          <Globe2 className="h-4 w-4" />
          <span>NBO → FRA/AMS</span>
        </div>
      </div>
    </motion.div>
  )
}

function DataPoint({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between p-2 bg-emerald-50/50 rounded border border-emerald-100">
      <span className="text-slate-600 text-xs uppercase tracking-wide">{label}</span>
      <span className="text-emerald-700 font-mono font-semibold text-xs">{value}</span>
    </div>
  )
}

function SatelliteView({ ndvi }: { ndvi: number }) {
  useEffect(() => {
    const canvas = document.getElementById('sat-canvas') as HTMLCanvasElement
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')!
    canvas.width = canvas.offsetWidth
    canvas.height = canvas.offsetHeight
    
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
    gradient.addColorStop(0, '#0a3f0a')
    gradient.addColorStop(0.3, '#1a5f1a')
    gradient.addColorStop(0.6, '#2a7f2a')
    gradient.addColorStop(1, '#1a5f1a')
    
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.15)'
    ctx.lineWidth = 1
    for (let i = 0; i < canvas.height; i += 15) {
      ctx.beginPath()
      ctx.moveTo(0, i)
      ctx.lineTo(canvas.width, i + Math.sin(i * 0.1) * 5)
      ctx.stroke()
    }
    
    for (let i = 0; i < 6; i++) {
      const x = Math.random() * canvas.width
      const y = Math.random() * canvas.height
      const radius = 20 + Math.random() * 30
      
      const health = ndvi + (Math.random() - 0.5) * 0.1
      const healthColor = health > 0.7 ? 'rgba(136, 255, 0, 0.4)' : 
                         health > 0.6 ? 'rgba(255, 255, 0, 0.3)' : 'rgba(255, 136, 0, 0.3)'
      
      const veg = ctx.createRadialGradient(x, y, 0, x, y, radius)
      veg.addColorStop(0, healthColor)
      veg.addColorStop(1, 'transparent')
      ctx.fillStyle = veg
      ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2)
    }
  }, [ndvi])

  return <canvas id="sat-canvas" className="w-full h-full" />
}

function CropsAndSeasons() {
  const crops = [
    { icon: <Salad className="h-5 w-5" />, name: "French Beans (Star 2008)", notes: "Extra/Super/Fine grades", seasons: "Peaks Oct-Mar, May-Jul" },
    { icon: <FlameKindling className="h-5 w-5" />, name: "Chili (Cayenne)", notes: "Sun-ripened, export grade", seasons: "Year-round peaks" },
    { icon: <Grape className="h-5 w-5" />, name: "Passion Fruit", notes: "Purple • Aroma-rich", seasons: "Near year-round" },
    { icon: <TreePine className="h-5 w-5" />, name: "Macadamia", notes: "Hand-picked", seasons: "Mar-Jun" },
  ]

  return (
    <section className="py-16 bg-gradient-to-b from-white to-emerald-50/60 border-y border-emerald-100 z-10 relative">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3 mb-8">
          <h3 className="text-3xl md:text-4xl font-bold">Crops & seasons</h3>
          <div className="text-sm text-emerald-800/80">Regions: Kenya (Eldoret, Uasin Gishu) • EU hub: NL & NRW • US intake: NJ</div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {crops.map((crop, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="bg-white border border-emerald-100 rounded-2xl p-5 hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <div className="flex items-center gap-3 text-emerald-800 mb-3">
                {crop.icon}
                <h4 className="font-semibold">{crop.name}</h4>
              </div>
              <div className="text-xs text-slate-600 mb-3">{crop.notes}</div>
              <div className="text-sm text-slate-700">{crop.seasons}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function HowItWorks() {
  const steps = [
    { title: "Farm", body: "Field protocols, irrigation, and harvest windows planned for grade and yield.", k: "GPS verified" },
    { title: "Packhouse", body: "Sorting, grading, cooling, and lot creation for export.", k: "QC lots" },
    { title: "Cold-chain", body: "4-6°C handling, route selection, and milestones tracked.", k: "On-time" },
    { title: "Arrival", body: "EU intake, residue checks, buyer delivery with trace link.", k: "Trace link" },
  ]

  return (
    <section className="py-20 z-10 relative">
      <div className="mx-auto max-w-7xl px-6">
        <h3 className="text-3xl md:text-4xl font-bold mb-4">How it works</h3>
        <p className="text-lg text-slate-700 max-w-2xl mb-12">From field to fork in four clean steps — always visible, always accountable.</p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.15 }}
              className="bg-white border border-emerald-100 rounded-2xl p-6 hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <div className="text-lg font-semibold text-emerald-700 mb-3">{step.title}</div>
              <div className="text-sm text-slate-700 mb-4">{step.body}</div>
              <div className="inline-flex items-center gap-2 text-xs text-emerald-800/90">
                <CheckCircle2 className="h-3.5 w-3.5" /> {step.k}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function ImpactAssurance() {
  const m1 = useCountUp(98)
  const m2 = useCountUp(36)
  const m3 = useCountUp(120)
  const m4 = useCountUp(92)

  return (
    <section className="py-16 bg-emerald-50/70 border-y border-emerald-100 z-10 relative">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <Metric label="On-time shipments" value={m2.value} suffix="h avg ETA" refEl={m2.ref} />
          <Metric label="CO₂ transparency" value={m1.value} suffix="% lots" refEl={m1.ref} />
          <Metric label="Farms in network" value={m3.value} suffix="+" refEl={m3.ref} />
          <Metric label="Residue compliance" value={m4.value} suffix="%" refEl={m4.ref} />
        </div>
      </div>
    </section>
  )
}

function Metric({ label, value, suffix, refEl }: { label: string; value: number; suffix?: string; refEl: React.RefObject<HTMLDivElement> }) {
  return (
    <div ref={refEl} className="bg-white border border-emerald-100 rounded-2xl p-6 text-center">
      <div className="text-xs text-slate-600 mb-2">{label}</div>
      <div className="text-3xl font-bold text-emerald-700">
        {value.toLocaleString()} 
        <span className="text-base font-medium text-emerald-600 ml-1">{suffix}</span>
      </div>
    </div>
  )
}

function FinalCTA() {
  return (
    <section className="py-20 z-10 relative">
      <div className="mx-auto max-w-7xl px-6 grid md:grid-cols-2 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-white border border-emerald-100 rounded-2xl p-8"
        >
          <h4 className="text-2xl font-bold text-emerald-800 mb-4">For Buyers</h4>
          <p className="text-slate-700 mb-6">Source consistent quality with full traceability, residue controls, and reliable cold-chain.</p>
          <Link 
            href="/buyers" 
            className="inline-block px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-medium transition-colors"
          >
            Talk to Sourcing
          </Link>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-white border border-emerald-100 rounded-2xl p-8"
        >
          <h4 className="text-2xl font-bold text-emerald-800 mb-4">For Investors</h4>
          <p className="text-slate-700 mb-6">Back scalable, carbon-aware farming with clear use-of-funds and transparent returns.</p>
          <Link 
            href="/contact" 
            className="inline-block px-6 py-3 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-xl font-medium transition-colors"
          >
            Explore Investment
          </Link>
        </motion.div>
      </div>
    </section>
  )
}

function DataStream() {
  return (
    <div className="fixed bottom-0 left-0 w-full bg-gradient-to-t from-slate-900/95 to-slate-900/85 border-t-2 border-emerald-400 py-2 overflow-hidden z-50">
      <div className="flex animate-scroll whitespace-nowrap">
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🌍 FARM: GSG-KE-UG_Eldoret
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          📍 GPS: 0.5143°N, 35.2698°E
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🌾 HARVEST: French Beans 1,200kg/week
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          📊 GRADE: 62% Extra Fine, 28% Super Fine
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🏭 PACKHOUSE: Eldoret Cooling Facility
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          ❄️ PRE-COOL: 6°C Maintained
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          📋 KEPHIS: #KE/2024/FB/3847
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          ✅ GLOBALG.A.P: 4049929274838
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          ✈️ EXPORT: KQ516 to Amsterdam
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          📦 AWB: 180-58374629
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🌡️ FIELD TEMP: 22°C
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          💧 HUMIDITY: 58% Optimal
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🛰️ SATELLITE: Sentinel-2 Coverage
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          🌱 NDVI: 0.71 Healthy Vegetation
        </span>
        <span className="px-8 font-mono text-sm text-emerald-400 flex items-center gap-2">
          ☀️ WEATHER: Clear Skies
        </span>
      </div>
      
      <style jsx>{`
        @keyframes scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-scroll {
          animation: scroll 45s linear infinite;
        }
      `}</style>
    </div>
  )
}