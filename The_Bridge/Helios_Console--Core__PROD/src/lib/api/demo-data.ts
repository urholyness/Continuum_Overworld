import { OpsMetric, TraceEvent, Farm, Agent } from "./schemas";

// Demo data for local development
export const DEMO_OPS_METRICS: OpsMetric[] = [
  {
    kpi: "throughput_tph",
    value: 2.1,
    unit: "t/h",
    ts: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    org: "org-main"
  },
  {
    kpi: "efficiency_pct",
    value: 94.5,
    unit: "%",
    ts: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
    org: "org-main"
  },
  {
    kpi: "orders_open",
    value: 7,
    unit: "count",
    ts: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
    org: "org-main"
  },
  {
    kpi: "cost_per_unit_usd",
    value: 1.87,
    unit: "USD",
    ts: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    org: "org-main"
  },
  {
    kpi: "uptime_pct",
    value: 99.2,
    unit: "%",
    ts: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    org: "org-main"
  },
  {
    kpi: "queue_depth",
    value: 23,
    unit: "items",
    ts: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    org: "org-main"
  }
];

export const DEMO_TRACE_EVENTS: TraceEvent[] = [
  {
    id: "trace_001",
    ts: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    type: "supply_chain",
    actor: "farm_001",
    payload: {
      action: "harvest_completed",
      farm_id: "farm_001",
      batch_id: "batch_2023_001",
      quantity: "2.5t",
      quality_grade: "A+",
      location: { lat: -1.2921, lng: 36.8219 }
    }
  },
  {
    id: "trace_002",
    ts: new Date(Date.now() - 90 * 60 * 1000).toISOString(),
    type: "processing",
    actor: "agent_002",
    payload: {
      action: "quality_assessment",
      batch_id: "batch_2023_001",
      defects_found: 3,
      grade_assigned: "A+",
      inspector: "agent_002"
    }
  },
  {
    id: "trace_003",
    ts: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    type: "logistics",
    actor: "agent_006",
    payload: {
      action: "shipment_dispatched",
      batch_id: "batch_2023_001",
      destination: "Nairobi Processing Center",
      carrier: "Kenya Transport Ltd",
      tracking_id: "KT2023090001"
    }
  },
  {
    id: "trace_004",
    ts: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    type: "blockchain",
    actor: "agent_004",
    payload: {
      action: "anchor_created",
      batch_id: "batch_2023_001",
      transaction_hash: "0x1234...5678",
      block_number: 1234567,
      gas_used: 142000
    }
  },
  {
    id: "trace_005",
    ts: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    type: "market",
    actor: "agent_007",
    payload: {
      action: "price_updated",
      commodity: "arabica_coffee",
      price_usd: 4.25,
      price_change_pct: 2.1,
      volume_traded: "150t"
    }
  }
];

export const DEMO_FARMS: Farm[] = [
  {
    id: "farm_001",
    name: "Kiambu Highlands Coffee Estate",
    region: "Kiambu County",
    hectares: 125.5,
    status: "active"
  },
  {
    id: "farm_002", 
    name: "Nyeri Specialty Arabica Farm",
    region: "Nyeri County",
    hectares: 89.2,
    status: "active"
  },
  {
    id: "farm_003",
    name: "Mount Kenya Organic Collective",
    region: "Embu County", 
    hectares: 203.7,
    status: "active"
  },
  {
    id: "farm_004",
    name: "Thika Valley Cooperative",
    region: "Kiambu County",
    hectares: 156.8,
    status: "paused"
  },
  {
    id: "farm_005",
    name: "Muranga Sustainable Coffee",
    region: "Muranga County",
    hectares: 78.3,
    status: "active"
  }
];

export const DEMO_AGENTS: Agent[] = [
  {
    id: "agent_001",
    name: "Satellite Data Processor",
    role: "processor",
    tier: "T1",
    status: "online"
  },
  {
    id: "agent_002",
    name: "Quality Analyzer",
    role: "analyzer", 
    tier: "T2",
    status: "online"
  },
  {
    id: "agent_003",
    name: "Weather Aggregator",
    role: "aggregator",
    tier: "T1", 
    status: "degraded"
  },
  {
    id: "agent_004",
    name: "Blockchain Anchor",
    role: "anchor",
    tier: "T1",
    status: "online"
  },
  {
    id: "agent_005",
    name: "Farm Monitor", 
    role: "monitor",
    tier: "T2",
    status: "online"
  },
  {
    id: "agent_006",
    name: "Supply Chain Tracker",
    role: "tracker",
    tier: "T1",
    status: "online"
  },
  {
    id: "agent_007",
    name: "Market Price Oracle",
    role: "oracle",
    tier: "T2", 
    status: "online"
  },
  {
    id: "agent_008",
    name: "Carbon Calculator",
    role: "calculator",
    tier: "T2",
    status: "degraded"
  }
];

export const DEMO_PUBLIC_HIGHLIGHTS = {
  items: [
    {
      id: "highlight_001",
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      type: "supply_chain",
      summary: "Large batch harvest completed - 2.5t arabica coffee processed with A+ quality grade"
    },
    {
      id: "highlight_002", 
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      type: "sustainability",
      summary: "Carbon footprint reduced by 12% through optimized logistics and processing"
    },
    {
      id: "highlight_003",
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      type: "market",
      summary: "Market price for specialty arabica increased 2.1% driven by quality improvements"
    }
  ],
  note: "Data has been anonymized and aggregated for public consumption. Individual farm and transaction details are not included."
};