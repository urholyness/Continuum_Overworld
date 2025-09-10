import { apiFetch } from "./http";
import { Farm, Agent } from "./schemas";
import { z } from "zod";
import { logger } from "@/lib/utils/logger";
import { DEMO_FARMS, DEMO_AGENTS } from "./demo-data";

export async function listFarms(): Promise<Farm[]> {
  // Use demo data in demo mode
  if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
    logger.info('Using demo farms data');
    return DEMO_FARMS;
  }

  try {
    const data = await apiFetch<unknown>(`/admin/farms`);
    const farms = z.array(Farm).parse(data);
    logger.info('Successfully fetched farms', { count: farms.length });
    return farms;
  } catch (error) {
    logger.error('Failed to fetch farms', { 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    throw error;
  }
}

export async function upsertFarm(body: Partial<Farm> & { id: string; name: string }): Promise<Farm> {
  try {
    const data = await apiFetch<unknown>(`/admin/farms`, {
      method: "POST",
      body: JSON.stringify(body),
    });
    const farm = Farm.parse(data);
    logger.info('Successfully upserted farm', { farmId: farm.id, farmName: farm.name });
    return farm;
  } catch (error) {
    logger.error('Failed to upsert farm', { 
      farmId: body.id,
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    throw error;
  }
}

export async function listAgents(): Promise<Agent[]> {
  // Use demo data in demo mode
  if (process.env.NEXT_PUBLIC_DEMO_MODE === 'true') {
    logger.info('Using demo agents data');
    return DEMO_AGENTS;
  }

  try {
    const data = await apiFetch<unknown>(`/admin/agents`);
    const agents = z.array(Agent).parse(data);
    logger.info('Successfully fetched agents', { count: agents.length });
    return agents;
  } catch (error) {
    logger.error('Failed to fetch agents', { 
      error: error instanceof Error ? error.message : 'Unknown error' 
    });
    throw error;
  }
}