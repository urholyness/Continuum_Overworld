import { apiFetch } from '@/lib/api/http';
import { getOpsMetrics } from '@/lib/api/composer';
import { listFarms, listAgents } from '@/lib/api/admin';

// Mock fetch
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

describe('API Client', () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  describe('apiFetch', () => {
    it('should make successful API requests', async () => {
      const mockData = { test: 'data' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockData),
        status: 200,
      } as Response);

      const result = await apiFetch('/test');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
          cache: 'no-store',
        })
      );
      expect(result).toEqual(mockData);
    });

    it('should handle API errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: () => Promise.resolve('Not Found'),
      } as Response);

      await expect(apiFetch('/not-found')).rejects.toThrow('[API 404] Not Found');
    });
  });

  describe('Composer API', () => {
    it('should fetch ops metrics with proper validation', async () => {
      const mockMetrics = [
        {
          kpi: 'test_metric',
          value: 42,
          unit: 'units',
          ts: '2023-01-01T00:00:00.000Z',
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockMetrics),
        status: 200,
      } as Response);

      const result = await getOpsMetrics();
      
      expect(result).toEqual(mockMetrics);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/composer/ops/metrics'),
        expect.any(Object)
      );
    });

    it('should validate ops metrics schema', async () => {
      const invalidMetrics = [
        {
          kpi: 'test_metric',
          // missing required fields
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(invalidMetrics),
        status: 200,
      } as Response);

      await expect(getOpsMetrics()).rejects.toThrow();
    });
  });

  describe('Admin API', () => {
    it('should fetch farms list', async () => {
      const mockFarms = [
        {
          id: 'farm1',
          name: 'Test Farm',
          region: 'Test Region',
          hectares: 10,
          status: 'active' as const,
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockFarms),
        status: 200,
      } as Response);

      const result = await listFarms();
      
      expect(result).toEqual(mockFarms);
    });

    it('should fetch agents list', async () => {
      const mockAgents = [
        {
          id: 'agent1',
          name: 'Test Agent',
          role: 'processor',
          tier: 'T1',
          status: 'online' as const,
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAgents),
        status: 200,
      } as Response);

      const result = await listAgents();
      
      expect(result).toEqual(mockAgents);
    });
  });
});