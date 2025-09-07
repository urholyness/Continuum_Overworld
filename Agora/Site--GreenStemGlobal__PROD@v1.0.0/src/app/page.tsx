export default function Home() {
  return (
    <section className="grid gap-6">
      <h1 className="text-3xl font-semibold">From Leaf to Root — Traceable Freshness</h1>
      <p>Export‑grade produce from East Africa, verified and traceable end‑to‑end.</p>
      <div className="grid md:grid-cols-2 gap-4">
        <a className="p-4 border rounded-xl bg-white" href="/buyers">For Buyers →</a>
        <a className="p-4 border rounded-xl bg-white" href="/investors">For Investors →</a>
      </div>
    </section>
  );
}