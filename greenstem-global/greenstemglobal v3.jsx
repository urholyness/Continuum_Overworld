import React, { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Leaf, Sprout, Truck, Store, Factory, CheckCircle2, Recycle, Gauge, Salad, TreePine, Grape, FlameKindling, Globe2, ThermometerSun, Droplets } from "lucide-react";

// --- Utility: animated counter (on-enter) ---
function useCountUp(target: number, duration = 1500) {
  const [value, setValue] = useState(0);
  const started = useRef(false);
  const ref = useRef<HTMLDivElement | null>(null);
  const inView = useInView(ref, { margin: "0px 0px -20% 0px" });
  useEffect(() => {
    if (!inView || started.current) return;
    started.current = true;
    const t0 = performance.now();
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / duration);
      setValue(Math.floor(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, target, duration]);
  return { ref, value } as const;
}

// --- Fresh photo chips (placeholders for real crop photos) ---
const PhotoChip = ({ label, gradient }: { label: string; gradient: string }) => (
  <div className="group flex flex-col items-center">
    <div className={`h-20 w-20 rounded-full ${gradient} shadow-sm ring-1 ring-emerald-200/40`} />
    <span className="mt-2 text-xs text-slate-600 group-hover:text-slate-800">{label}</span>
  </div>
);

// --- One‑page landing ---
export default function GreenStemGlobalV2() {
  return (
    <div className="min-h-screen w-full bg-[#F7FBF5] text-slate-800 selection:bg-emerald-200/60 selection:text-emerald-900">
      <HeroSection />
      <DividerLeaf />
      <WhatWeDo />
      <CropsAndSeasons />
      <HowItWorks />
      <ImpactAssurance />
      <TrustRow />
      <FinalCTA />
      <Footer />
    </div>
  );
}

function HeroSection() {
  return (
    <section className="relative overflow-hidden">
      {/* Sunlit background */}
      <div className="absolute inset-0 bg-gradient-to-b from-emerald-50 via-emerald-50 to-white" />
      <div className="absolute -top-24 -right-24 h-80 w-80 rounded-full bg-emerald-200/40 blur-3xl" />
      <div className="absolute -bottom-24 -left-24 h-80 w-80 rounded-full bg-lime-200/40 blur-3xl" />

      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-28 pb-12 md:pt-36 md:pb-20 grid md:grid-cols-2 gap-10">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-white/80 ring-1 ring-emerald-200 px-3 py-1 text-xs text-emerald-700">
            <Leaf className="h-3.5 w-3.5" /> Global farming • EU‑grade quality • Real traceability
          </div>
          <h1 className="mt-5 text-4xl sm:text-6xl font-semibold leading-tight tracking-tight">
            Global farming, <span className="bg-clip-text text-transparent bg-gradient-to-r from-emerald-600 to-lime-600">traceable by design</span>.
          </h1>
          <p className="mt-4 text-lg text-slate-700 max-w-xl">
            We grow and source fresh produce across East Africa and deliver it to Europe & the US with verifiable quality, cold‑chain integrity, and carbon accounting.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button className="rounded-xl px-6 py-5 bg-emerald-600 hover:bg-emerald-500 text-white">I'm a Buyer</Button>
            <Button variant="secondary" className="rounded-xl px-6 py-5 bg-white hover:bg-emerald-50 text-emerald-800 border border-emerald-200">I'm an Investor</Button>
          </div>
          {/* crop chips */}
          <div className="mt-8 flex items-center gap-5">
            <PhotoChip label="French Beans" gradient="bg-gradient-to-br from-emerald-300 to-emerald-500" />
            <PhotoChip label="Chili" gradient="bg-gradient-to-br from-orange-300 to-red-400" />
            <PhotoChip label="Passion Fruit" gradient="bg-gradient-to-br from-fuchsia-300 to-purple-400" />
            <PhotoChip label="Macadamia" gradient="bg-gradient-to-br from-amber-300 to-amber-500" />
          </div>
        </div>
        {/* right visual */}
        <div className="md:pl-6">
          <HeroCard />
        </div>
      </div>
    </section>
  );
}

function HeroCard() {
  const items = [
    { icon: <ThermometerSun className="h-4 w-4" />, k: "4–6°C", v: "Cold‑chain maintained" },
    { icon: <Droplets className="h-4 w-4" />, k: "Residue", v: "EU limits observed" },
    { icon: <Globe2 className="h-4 w-4" />, k: "Routes", v: "NBO → FRA / AMS" },
  ];
  return (
    <Card className="bg-white/80 backdrop-blur border-emerald-100 shadow-lg rounded-2xl">
      <CardContent className="p-6">
        <div className="aspect-[4/3] w-full rounded-xl bg-gradient-to-br from-emerald-100 to-lime-100 grid place-items-center text-sm text-emerald-700">
          <div className="grid grid-cols-2 gap-4 w-full px-6">
            <div className="rounded-lg bg-white/70 ring-1 ring-emerald-100 p-3">
              <div className="text-xs text-emerald-700">Farm • Uasin Gishu</div>
              <div className="text-sm font-medium">GPS: −0.379, 35.285</div>
            </div>
            <div className="rounded-lg bg-white/70 ring-1 ring-emerald-100 p-3">
              <div className="text-xs text-emerald-700">Shipment</div>
              <div className="text-sm font-medium">ETA: 36h • AWB #784‑221</div>
            </div>
            <div className="rounded-lg bg-white/70 ring-1 ring-emerald-100 p-3">
              <div className="text-xs text-emerald-700">Quality</div>
              <div className="text-sm font-medium">QC lot #118 • 0.0% rejects</div>
            </div>
            <div className="rounded-lg bg-white/70 ring-1 ring-emerald-100 p-3">
              <div className="text-xs text-emerald-700">Carbon</div>
              <div className="text-sm font-medium">86 kg/ton estimate</div>
            </div>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-3 gap-3">
          {items.map((x, i) => (
            <div key={i} className="flex items-center gap-2 text-emerald-800 text-xs">
              {x.icon}
              <span className="font-medium">{x.k}</span>
              <span className="text-slate-600">{x.v}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function DividerLeaf() {
  return (
    <div className="mx-auto max-w-7xl px-6 mt-6 md:mt-2">
      <div className="flex items-center gap-3 text-emerald-700/80">
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent" />
        <Leaf className="h-4 w-4" />
        <div className="h-px flex-1 bg-gradient-to-r from-transparent via-emerald-300 to-transparent" />
      </div>
    </div>
  );
}

function WhatWeDo() {
  const tiles = [
    { icon: <Sprout className="h-5 w-5" />, title: "We Grow", body: "Own and partner farms across Kenya with field protocols and crop rotation." },
    { icon: <Factory className="h-5 w-5" />, title: "We Pack & Aggregate", body: "Sorting, grading, and export prep in EU‑aligned pack processes." },
    { icon: <CheckCircle2 className="h-5 w-5" />, title: "We Assure Quality", body: "Residue testing, GlobalG.A.P. pathway, and shipment QC lots." },
    { icon: <Truck className="h-5 w-5" />, title: "We Move Cold‑Chain", body: "4–6°C handling, fast routes NBO → FRA/AMS, on‑time coordination." },
    { icon: <Gauge className="h-5 w-5" />, title: "We Trace & Report", body: "Lot‑level traceability with farm GPS, temp trail, and carbon estimate." },
    { icon: <Recycle className="h-5 w-5" />, title: "We Steward Impact", body: "Water‑wise irrigation, soil health, and livelihoods for growers." },
  ];
  return (
    <section className="py-14 md:py-20">
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="text-3xl md:text-5xl font-semibold tracking-tight">What we do</h2>
        <p className="mt-3 text-slate-700 max-w-2xl">GreenStemGlobal is a global farming company: production, aggregation, quality, logistics, and transparent data — on one clean rail.</p>
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {tiles.map((t, i) => (
            <Card key={i} className="bg-white border-emerald-100 hover:shadow-md transition rounded-2xl">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 text-emerald-800">{t.icon}<span className="text-lg font-medium">{t.title}</span></div>
                <p className="mt-2 text-slate-700 text-sm">{t.body}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function CropsAndSeasons() {
  const crops = [
    { icon: <Salad className="h-5 w-5" />, name: "French Beans (Star 2005/2008)", notes: "Extra/Super/Fine grades", seasons: "Peaks Oct–Mar, May–Jul" },
    { icon: <FlameKindling className="h-5 w-5" />, name: "Chili (Cayenne)", notes: "Sun‑ripened, export grade", seasons: "Year‑round peaks" },
    { icon: <Grape className="h-5 w-5" />, name: "Passion Fruit", notes: "Purple • Aroma‑rich", seasons: "Near year‑round" },
    { icon: <TreePine className="h-5 w-5" />, name: "Macadamia", notes: "Hand‑picked", seasons: "Mar–Jun" },
  ];
  return (
    <section className="py-12 md:py-16 bg-gradient-to-b from-white to-emerald-50/60 border-y border-emerald-100">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
          <h3 className="text-2xl md:text-3xl font-semibold">Crops & seasons</h3>
          <div className="text-sm text-emerald-800/80">Regions: Kenya (Uasin Gishu, Kiambu) • EU hub: NRW & NL • US intake: NJ</div>
        </div>
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {crops.map((c, i) => (
            <Card key={i} className="bg-white border-emerald-100 rounded-2xl">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-emerald-800">{c.icon}<span className="font-medium">{c.name}</span></div>
                <div className="mt-2 text-xs text-slate-600">{c.notes}</div>
                <div className="mt-3 text-sm text-slate-700">{c.seasons}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { title: "Farm", body: "Field protocols, irrigation, and harvest windows planned for grade and yield.", k: "GPS verified" },
    { title: "Packhouse", body: "Sorting, grading, cooling, and lot creation for export.", k: "QC lots" },
    { title: "Cold‑chain", body: "4–6°C handling, route selection, and milestones tracked.", k: "On‑time" },
    { title: "Arrival", body: "EU intake, residue checks, buyer delivery with trace link.", k: "Trace link" },
  ];
  return (
    <section className="py-14 md:py-20">
      <div className="mx-auto max-w-7xl px-6">
        <h3 className="text-2xl md:text-3xl font-semibold">How it works</h3>
        <p className="mt-2 text-slate-700 max-w-2xl">From field to fork in four clean steps — always visible, always accountable.</p>
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          {steps.map((s, i) => (
            <Card key={i} className="bg-white border-emerald-100 rounded-2xl">
              <CardContent className="p-5">
                <div className="text-sm text-emerald-700 font-medium">{s.title}</div>
                <div className="mt-2 text-sm text-slate-700">{s.body}</div>
                <div className="mt-3 inline-flex items-center gap-1 text-xs text-emerald-800/90">
                  <CheckCircle2 className="h-3.5 w-3.5" /> {s.k}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}

function ImpactAssurance() {
  const m1 = useCountUp(98);
  const m2 = useCountUp(36);
  const m3 = useCountUp(120);
  const m4 = useCountUp(92);
  return (
    <section className="py-12 md:py-16 bg-emerald-50/70 border-y border-emerald-100">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Metric label="On‑time shipments" value={m2.value} suffix="h avg ETA" refEl={m2.ref} />
          <Metric label="CO₂ transparency" value={m1.value} suffix="% lots" refEl={m1.ref} />
          <Metric label="Farms in network" value={m3.value} suffix="+" refEl={m3.ref} />
          <Metric label="Residue compliance" value={m4.value} suffix="%" refEl={m4.ref} />
        </div>
        <p className="mt-3 text-xs text-slate-600">*Illustrative counters — connect to live ops later.</p>
      </div>
    </section>
  );
}

function Metric({ label, value, suffix, refEl }: { label: string; value: number; suffix?: string; refEl: React.RefObject<HTMLDivElement> }) {
  return (
    <Card ref={refEl as any} className="bg-white border-emerald-100 rounded-2xl">
      <CardContent className="p-5">
        <div className="text-xs text-slate-600">{label}</div>
        <div className="mt-1 text-3xl font-semibold text-emerald-700">{value.toLocaleString()} <span className="text-base font-medium text-emerald-600">{suffix}</span></div>
      </CardContent>
    </Card>
  );
}

function TrustRow() {
  return (
    <section className="py-10">
      <div className="mx-auto max-w-7xl px-6">
        <div className="text-sm text-emerald-800/90">Certifications & partners</div>
        <div className="mt-4 grid grid-cols-3 sm:grid-cols-6 gap-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-12 rounded-md bg-white ring-1 ring-emerald-100 grid place-items-center text-[10px] text-emerald-700/70">LOGO</div>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500">Swap placeholders with GlobalG.A.P., ISO, KEPHIS, EU Organic, carriers & buyers.</p>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section className="py-16">
      <div className="mx-auto max-w-7xl px-6 grid md:grid-cols-2 gap-6">
        <Card className="bg-white border-emerald-100 rounded-2xl">
          <CardContent className="p-6 md:p-8">
            <h4 className="text-2xl font-semibold text-emerald-800">For Buyers</h4>
            <p className="mt-2 text-slate-700">Source consistent quality with full traceability, residue controls, and reliable cold‑chain.</p>
            <Button className="mt-6 rounded-xl bg-emerald-600 hover:bg-emerald-500">Talk to Sourcing</Button>
          </CardContent>
        </Card>
        <Card className="bg-white border-emerald-100 rounded-2xl">
          <CardContent className="p-6 md:p-8">
            <h4 className="text-2xl font-semibold text-emerald-800">For Investors</h4>
            <p className="mt-2 text-slate-700">Back scalable, carbon‑aware farming with clear use‑of‑funds and transparent returns.</p>
            <Button variant="secondary" className="mt-6 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200">Explore Tracks</Button>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-emerald-100 py-8 bg-white/70">
      <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-emerald-800/90">
        <div>© GreenStemGlobal — From Seed to Shelf.</div>
        <div className="flex items-center gap-4">
          <a className="hover:text-emerald-700" href="#buyers">Buyers</a>
          <a className="hover:text-emerald-700" href="#investors">Investors</a>
          <a className="hover:text-emerald-700" href="#about">About</a>
          <a className="hover:text-emerald-700" href="#contact">Contact</a>
        </div>
      </div>
    </footer>
  );
}
