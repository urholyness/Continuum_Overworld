export default function LotCard({ lot }: { lot: any }) {
  return (
    <article className="p-4 border rounded-xl bg-white">
      <div className="flex items-baseline justify-between">
        <h3 className="font-medium">{lot.lot_id}</h3>
        <span className="text-xs text-neutral-600">{lot.crop}</span>
      </div>
      <div className="mt-2 text-sm">
        <div>Farm: {lot.origin.farm}</div>
        <div>NDVI: {lot.indices.ndvi} · NDWI: {lot.indices.ndwi}</div>
        <div>CO₂e: {lot.co2e_kg} kg</div>
      </div>
      <ol className="mt-3 border-l pl-4 space-y-2">
        {lot.events.map((e: any, i: number) => (
          <li key={i}>
            <div className="text-sm">{e.type}</div>
            <div className="text-xs text-neutral-600">{e.ts}</div>
          </li>
        ))}
      </ol>
    </article>
  );
}