import { extractFromPDF } from "./kpi_context.js";
import { strict as assert } from "node:assert";
test("extract returns at least one KPI and one Context", async () => {
  const r = await extractFromPDF("/tmp/mock.pdf", "https://example.com", "deadbeef");
  assert.ok(r.kpis.length >= 1); assert.ok(r.contexts.length >= 1);
});