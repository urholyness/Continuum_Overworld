interface Params { params: { id: string } }

export default async function TraceDetail({ params }: Params) {
  const id = params.id;
  const base = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
  // FUTURE: choose endpoint by prefix (0x.. onchain vs lot id)
  const res = await fetch(`${base}/api/trace/lots`, { cache: "no-store" });
  const all = await res.json();
  const lot = all.find((l: any) => l.lot_id === id) || null;
  
  return (
    <section className="grid gap-4">
      <h2 className="text-2xl font-semibold">Trace Detail</h2>
      {!lot ? (
        <p className="text-sm text-neutral-600">No record for <code>{id}</code></p>
      ) : (
        <pre className="p-4 bg-white border rounded-xl overflow-auto text-xs">
{JSON.stringify(lot, null, 2)}
        </pre>
      )}
    </section>
  );
}