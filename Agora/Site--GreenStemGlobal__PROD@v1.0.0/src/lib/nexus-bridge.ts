/**
 * Nexus Bridge - Connects C_O development to C_N cloud
 * Following Agora/Playbook--WebDev__PROD@v2.0.0
 * All cloud resources use C_N:: prefix
 */

export interface ContinuumConfig {
  local: {
    prefix: string;
    environment: string;
    realm: string;
  };
  cloud: {
    prefix: string;
    environment: string;
    region: string;
    orchestrator: string;
  };
  resources: {
    eventBus: string;
    farmMetricsTable: string;
    traceEventsTable: string;
    pantheonRegistry: string;
    opsMetricsTable: string;
    dataLakeBucket: string;
    traceArchiveBucket: string;
  };
  apis: {
    composer: string;
    admin: string;
    trace: string;
  };
}

export const NexusConfig: ContinuumConfig = {
  local: {
    prefix: 'C_O',
    environment: 'development',
    realm: 'Continuum_Overworld'
  },
  cloud: {
    prefix: 'C_N',
    environment: process.env.C_N_ENV || 'PROD',
    region: process.env.NEXT_PUBLIC_AWS_REGION || 'us-east-1',
    orchestrator: 'Continuum_Nexus'
  },
  resources: {
    eventBus: process.env.CORE_EVENT_BUS || 'C_N-EventBus-Core',
    farmMetricsTable: process.env.FARM_METRICS_TABLE || 'C_N-FarmMetrics-Live',
    traceEventsTable: process.env.TRACE_EVENTS_TABLE || 'C_N-TraceEvents-Stream',
    pantheonRegistry: process.env.AGENT_REGISTRY_TABLE || 'C_N-Pantheon-Registry',
    opsMetricsTable: process.env.OPS_METRICS_TABLE || 'C_N-Ops-Metrics',
    dataLakeBucket: process.env.DATA_LAKE_BUCKET || `c-n-data-lake-${process.env.AWS_ACCOUNT_ID}`,
    traceArchiveBucket: process.env.TRACE_ARCHIVE_BUCKET || `c-n-trace-archive-${process.env.AWS_ACCOUNT_ID}`
  },
  apis: {
    composer: process.env.NEXT_PUBLIC_API_BASE_URL + '/composer' || 'https://cn-api.greenstemglobal.com/composer',
    admin: process.env.NEXT_PUBLIC_API_BASE_URL + '/admin' || 'https://cn-api.greenstemglobal.com/admin',
    trace: process.env.NEXT_PUBLIC_API_BASE_URL + '/trace' || 'https://cn-api.greenstemglobal.com/trace'
  }
};

/**
 * Transform C_O resource names to C_N for cloud deployment
 * @param localResource - Local resource name with C_O prefix
 * @returns Cloud resource name with C_N prefix
 */
export function transformToNexus(localResource: string): string {
  // Remove C_O prefix and add C_N prefix
  const baseName = localResource.replace(/^C_O[-_]?/, '');
  return `C_N-${baseName}`;
}

/**
 * Transform C_N cloud resource names back to C_O for local development
 * @param cloudResource - Cloud resource name with C_N prefix
 * @returns Local resource name with C_O prefix
 */
export function transformFromNexus(cloudResource: string): string {
  // Remove C_N prefix and add C_O prefix
  const baseName = cloudResource.replace(/^C_N[-_]?/, '');
  return `C_O-${baseName}`;
}

/**
 * Get appropriate resource name based on environment
 * @param resourceType - Type of resource (table, bucket, etc.)
 * @param baseName - Base name without prefix
 * @returns Environment-appropriate resource name
 */
export function getResourceName(resourceType: 'table' | 'bucket' | 'function' | 'eventBus', baseName: string): string {
  const isDevelopment = process.env.NODE_ENV === 'development' || process.env.C_O_ENV === 'development';
  const prefix = isDevelopment ? 'C_O' : 'C_N';
  
  // Handle bucket naming (lowercase with account ID)
  if (resourceType === 'bucket') {
    const accountId = process.env.AWS_ACCOUNT_ID || 'dev';
    return `${prefix.toLowerCase()}-${baseName.toLowerCase()}-${accountId}`;
  }
  
  return `${prefix}-${baseName}`;
}

/**
 * Environment detection utilities
 */
export const Environment = {
  isDevelopment: () => process.env.NODE_ENV === 'development' || process.env.C_O_ENV === 'development',
  isProduction: () => process.env.NODE_ENV === 'production' || process.env.C_N_ENV === 'PROD',
  isDemo: () => process.env.NEXT_PUBLIC_DEMO_MODE === 'true',
  getCurrentRealm: () => Environment.isDevelopment() ? 'Continuum_Overworld' : 'Continuum_Nexus',
  getCurrentPrefix: () => Environment.isDevelopment() ? 'C_O' : 'C_N'
};

/**
 * API Client configuration with automatic environment detection
 */
export const ApiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cn-api.greenstemglobal.com',
  timeout: parseInt(process.env.API_TIMEOUT || '30000'),
  headers: {
    'Content-Type': 'application/json',
    'X-Continuum-Realm': Environment.getCurrentRealm(),
    'X-Continuum-Prefix': Environment.getCurrentPrefix()
  }
};

/**
 * Division mapping for resource routing
 */
export const DivisionMap = {
  'The_Bridge': 'C_N-Bridge',
  'Agora': 'C_N-Agora',
  'Forge': 'C_N-Forge',
  'Oracle': 'C_N-Oracle',
  'Pantheon': 'C_N-Pantheon',
  'Atlas': 'C_N-Atlas',
  'Aegis': 'C_N-Aegis',
  'Meridian': 'C_N-Meridian',
  'Ledger': 'C_N-Ledger'
} as const;

export type Division = keyof typeof DivisionMap;

/**
 * Get cloud division name from local division
 * @param localDivision - Local division name
 * @returns Cloud division name
 */
export function getCloudDivision(localDivision: Division): string {
  return DivisionMap[localDivision];
}

/**
 * Debug utilities for development
 */
export const Debug = {
  logConfig: () => {
    if (Environment.isDevelopment()) {
      console.group('🔧 Nexus Bridge Configuration');
      console.log('Current Realm:', Environment.getCurrentRealm());
      console.log('Current Prefix:', Environment.getCurrentPrefix());
      console.log('Demo Mode:', Environment.isDemo());
      console.log('API Base URL:', ApiConfig.baseUrl);
      console.log('Resources:', NexusConfig.resources);
      console.groupEnd();
    }
  },
  
  logTransformation: (original: string, transformed: string) => {
    if (Environment.isDevelopment()) {
      console.log(`🔄 Resource Transform: ${original} → ${transformed}`);
    }
  }
};

export default NexusConfig;