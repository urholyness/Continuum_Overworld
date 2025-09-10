import '@testing-library/jest-dom'

// Mock window.localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock fetch for API tests
global.fetch = jest.fn();

// Mock environment variables for tests
process.env.NEXT_PUBLIC_SITE_ENV = 'test';
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000';
process.env.NEXT_PUBLIC_WS_URL = 'ws://localhost:8001';
process.env.NEXT_PUBLIC_CHAIN_ID = '11155111';