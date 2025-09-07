export default function FundsTimeline({ data }: { data: any }) {
  const items = [
    { label: "Deposit", ts: data.investor_deposit.ts, amount: `$${data.investor_deposit.amount_usd}` },
    { label: "FX & Fees", ts: data.fx.ts, amount: `$${data.fx.fee_usd} fee @ ${data.fx.rate}` },
    { label: "Transfer KE", ts: data.transfer_ke.ts, amount: `${data.transfer_ke.amount_kes} KES` },
    ...data.allocations.map((a: any) => ({ label: `${a.category}`, ts: "", amount: `${a.amount_kes} KES` })),
  ];
  return (
    <ol className="border-l pl-4 space-y-3">
      {items.map((i, idx) => (
        <li key={idx}>
          <div className="font-medium">{i.label}</div>
          <div className="text-sm text-neutral-600">{i.ts}</div>
          <div className="text-sm">{i.amount}</div>
        </li>
      ))}
    </ol>
  );
}