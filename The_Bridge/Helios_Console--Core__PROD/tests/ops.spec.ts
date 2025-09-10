import { test, expect } from "@playwright/test";

test.describe('Operations Page', () => {
  test('should render operations page', async ({ page }) => {
    await page.goto('/ops');
    
    // Check that the main heading is visible
    await expect(page.getByText('Operations')).toBeVisible();
    
    // Check that the subtitle is visible
    await expect(page.getByText('Real-time operational metrics')).toBeVisible();
    
    // Wait for content to load (either metrics or error state)
    // Since we don't have a backend running, we expect either loading state or error
    await page.waitForTimeout(2000);
  });

  test('should have proper navigation', async ({ page }) => {
    await page.goto('/ops');
    
    // Check navigation links are present
    await expect(page.getByText('Helios Console')).toBeVisible();
    await expect(page.locator('a[href="/trace"]')).toBeVisible();
    await expect(page.locator('a[href="/agents"]')).toBeVisible();
    await expect(page.locator('a[href="/admin/farms"]')).toBeVisible();
  });
});

test.describe('Trace Page', () => {
  test('should render trace page', async ({ page }) => {
    await page.goto('/trace');
    
    await expect(page.getByText('Traceability')).toBeVisible();
    await expect(page.getByText('Event audit trail')).toBeVisible();
  });
});

test.describe('Agents Page', () => {
  test('should render agents page', async ({ page }) => {
    await page.goto('/agents');
    
    await expect(page.getByText('Agents')).toBeVisible();
    await expect(page.getByText('Monitor agent status and performance')).toBeVisible();
  });
});

test.describe('Admin Farms Page', () => {
  test('should render admin farms page', async ({ page }) => {
    await page.goto('/admin/farms');
    
    await expect(page.getByText('Farms Administration')).toBeVisible();
    await expect(page.getByText('Manage farm registrations and configurations')).toBeVisible();
  });
});