import { NextRequest } from "next/server";
import sample from "@/../mocks/funds_sample.json";

export async function GET(req: NextRequest) {
  const download = req.nextUrl.searchParams.get("download");
  const body = JSON.stringify(sample);
  return new Response(body, {
    status: 200,
    headers: {
      "content-type": "application/json",
      ...(download ? { "content-disposition": "attachment; filename=funds_audit.json" } : {}),
    },
  });
}