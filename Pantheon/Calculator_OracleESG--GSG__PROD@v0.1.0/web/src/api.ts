import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Batch {
  project_tag: string;
  commodity: string;
  net_mass_kg: number;
  packaging_mass_kg: number;
  harvest_week?: string;
  ownership: string;
}

export interface Leg {
  mode: string;
  from_loc: string;
  to_loc: string;
  distance_km: number;
  payload_t: number;
  load_factor_pct?: number;
  backhaul?: boolean;
  vehicle_class: string;
  energy_type?: string;
  energy_qty?: number;
  date?: string;
  data_quality: string;
  rf_apply?: boolean;
}

export interface Hub {
  type: string;
  kwh: number;
  energy_source: string;
  hours?: number;
  location?: string;
}

export const batchApi = {
  create: async (batch: Batch) => {
    const response = await api.post('/batches', batch);
    return response.data;
  },
  
  get: async (id: number) => {
    const response = await api.get(`/batches/${id}`);
    return response.data;
  },
  
  list: async () => {
    const response = await api.get('/batches');
    return response.data;
  },
  
  duplicate: async (id: number) => {
    const response = await api.post(`/batches/${id}/duplicate`);
    return response.data;
  },
};

export const legApi = {
  create: async (batchId: number, legs: Leg[]) => {
    const response = await api.post(`/batches/${batchId}/legs`, legs);
    return response.data;
  },
  
  list: async (batchId: number) => {
    const response = await api.get(`/batches/${batchId}/legs`);
    return response.data;
  },
};

export const hubApi = {
  create: async (batchId: number, hubs: Hub[]) => {
    const response = await api.post(`/batches/${batchId}/hubs`, hubs);
    return response.data;
  },
  
  list: async (batchId: number) => {
    const response = await api.get(`/batches/${batchId}/hubs`);
    return response.data;
  },
};

export const calculationApi = {
  calculate: async (batchId: number, factorPack = 'DEFRA-2024', rf = true) => {
    const response = await api.post(`/batches/${batchId}/calculate`, {
      factor_pack: factorPack,
      rf: rf,
    });
    return response.data;
  },
  
  getCbamSnippet: async (batchId: number) => {
    const response = await api.get(`/batches/${batchId}/cbam-snippet`);
    return response.data;
  },
  
  getLatestResults: async (batchId: number) => {
    const response = await api.get(`/batches/${batchId}/results/latest`);
    return response.data;
  },
};