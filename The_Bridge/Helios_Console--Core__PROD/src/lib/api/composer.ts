import { apiFetch } from "./http";
import { z } from "zod";
import { OpsMetric, TraceEventsResponse } from "./schemas";
import { logger } from "@/lib/utils/logger";
import { DEMO_OPS_METRICS, DEMO_TRACE_EVENTS } from "./demo-data";

export async function getOpsMetrics(org = 'org-main'): Promise<OpsMetric[]> {
  // Use demo data in demo mode
  if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
    logger.info('Using demo ops metrics data');
    return DEMO_OPS_METRICS;
  }

  try {
    const params = new URLSearchParams({ org });
    const data = await apiFetch<unknown>(`/composer/ops/metrics?${params}`);
    const metrics = z.array(OpsMetric).parse(data);
    logger.info('Successfully fetched ops metrics', { count: metrics.length });
    return metrics;
  } catch (error) {
    logger.error('Failed to fetch ops metrics', { 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    throw error;
  }
}

export async function getTraceEvents(params: { 
  org?: string; 
  from?: string; 
  to?: string; 
  limit?: number; 
  cursor?: string; 
}): Promise<TraceEventsResponse> {
  // Use demo data in demo mode
  if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
    logger.info('Using demo trace events data');
    return {
      items: DEMO_TRACE_EVENTS,
      nextCursor: null,
      total: DEMO_TRACE_EVENTS.length
    };
  }

  try {
    const queryParams = new URLSearchParams({
      org: params.org || 'org-main',
      ...(params.from && { from: params.from }),
      ...(params.to && { to: params.to }),
      ...(params.limit && { limit: params.limit.toString() }),
      ...(params.cursor && { cursor: params.cursor }),
    });

    const data = await apiFetch<unknown>(`/composer/trace/events?${queryParams}`);
    const response = TraceEventsResponse.parse(data);
    logger.info('Successfully fetched trace events', { 
      count: response.items.length,
      hasNextCursor: !!response.nextCursor 
    });
    return response;
  } catch (error) {
    logger.error('Failed to fetch trace events', { 
      params,
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    throw error;
  }
}