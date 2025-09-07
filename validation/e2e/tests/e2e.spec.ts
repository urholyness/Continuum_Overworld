import { test, expect } from '@playwright/test';

test('Public farm page is fresh and renders NDVI', async ({ page }) => {
  await page.goto('/farms/2BH');
  await expect(page.getByText(/Two Butterflies Homestead/i)).toBeVisible();
  await expect(page.getByTestId('freshness-weather')).toBeVisible();
  await expect(page.getByTestId('ndvi-thumbnail')).toBeVisible();
  await expect(page.getByTestId('farm-map')).toBeVisible();
});

