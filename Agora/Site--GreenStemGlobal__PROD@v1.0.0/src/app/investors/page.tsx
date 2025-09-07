import FundsTimeline from "@/components/FundsTimeline";
import BlockchainBreadcrumbs from "@/components/BlockchainBreadcrumbs";

async function fetchFunds() {
  const base = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
  const res = await fetch(`${base}/api/trace/funds`, { cache: "no-store" });
  return res.json();
}

export default async function Investors() {
  const data = await fetchFunds();
  return (
    <section className="grid gap-6">
      <h2 className="text-2xl font-semibold">Where Your Money Goes</h2>
      <div className="grid lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-medium mb-4">Fund Flow Timeline</h3>
          <FundsTimeline data={data} />
        </div>
        <div>
          <BlockchainBreadcrumbs />
        </div>
      </div>
      <a className="underline text-sm" href="/api/trace/funds?download=1">Download audit JSON</a>
    </section>
  );
}