import LotCard from "@/components/LotCard";

async function fetchLots() {
  const base = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
  const res = await fetch(`${base}/api/trace/lots`, { cache: "no-store" });
  return res.json();
}

export default async function Buyers() {
  const lots = await fetchLots();
  return (
    <section className="grid gap-6">
      <h2 className="text-2xl font-semibold">Traceability Highlights</h2>
      <div className="grid md:grid-cols-2 gap-4">
        {lots.map((l: any) => (
          <LotCard key={l.lot_id} lot={l} />
        ))}
      </div>
    </section>
  );
}