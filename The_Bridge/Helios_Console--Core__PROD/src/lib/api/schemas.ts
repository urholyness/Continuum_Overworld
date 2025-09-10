import { z } from "zod";

export const Farm = z.object({
  id: z.string(),
  name: z.string(),
  region: z.string(),
  hectares: z.number(),
  status: z.enum(["active", "paused"]),
  geometry: z.object({}).optional(), // GeoJSON Feature or Polygon
});
export type Farm = z.infer<typeof Farm>;

export const Agent = z.object({
  id: z.string(),
  name: z.string(),
  role: z.string(),
  tier: z.string(),
  status: z.enum(["online", "degraded", "offline"]),
});
export type Agent = z.infer<typeof Agent>;

export const OpsMetric = z.object({
  kpi: z.string(),
  value: z.number(),
  unit: z.string(),
  ts: z.string().datetime(),
  org: z.string(),
});
export type OpsMetric = z.infer<typeof OpsMetric>;

export const TraceEvent = z.object({
  id: z.string(),
  ts: z.string().datetime(),
  type: z.string(),
  actor: z.string().nullable(),
  payload: z.record(z.unknown()),
});
export type TraceEvent = z.infer<typeof TraceEvent>;

export const TraceEventsResponse = z.object({
  items: z.array(TraceEvent),
  nextCursor: z.string().nullable(),
  total: z.number(),
});
export type TraceEventsResponse = z.infer<typeof TraceEventsResponse>;