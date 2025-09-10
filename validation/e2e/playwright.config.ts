import { defineConfig } from '@playwright/test';
export default defineConfig({
  timeout: 60000,
  use: { baseURL: process.env.UI_BASE || 'http://localhost:3000' }
});




