import { getJWT } from "@/lib/auth/token";
import { logger } from "@/lib/utils/logger";

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!base) {
    throw new Error('NEXT_PUBLIC_API_BASE_URL environment variable is not set');
  }

  const url = `${base}${path}`;
  
  try {
    const authHeader = await getAuthHeader();
    const response = await fetch(url, {
      ...init,
      headers: {
        "content-type": "application/json",
        ...(init.headers || {}),
        ...(authHeader ? { authorization: authHeader } : {}),
      },
      cache: "no-store",
    });

    if (!response.ok) {
      const errorText = await response.text();
      const error = new Error(`[API ${response.status}] ${errorText}`);
      logger.error('API request failed', { 
        url, 
        status: response.status, 
        error: errorText 
      });
      throw error;
    }

    const data = await response.json() as T;
    logger.info('API request successful', { url, status: response.status });
    return data;
  } catch (error) {
    logger.error('API request error', { url, error: error instanceof Error ? error.message : 'Unknown error' });
    throw error;
  }
}

async function getAuthHeader(): Promise<string | null> {
  try {
    const jwt = await getJWT();
    return jwt ? `Bearer ${jwt}` : null;
  } catch (error) {
    logger.warn('Failed to get JWT token', { error: error instanceof Error ? error.message : 'Unknown error' });
    return null;
  }
}