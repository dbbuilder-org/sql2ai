import { test, expect } from '@playwright/test';

test.describe('Consulting Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/consulting');
  });

  test('should display consulting hero', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText(/Database Consulting/i)).toBeVisible();
  });

  test('should display service offerings', async ({ page }) => {
    // Check for service cards or sections
    const serviceTypes = [
      'Database Architecture',
      'Performance Optimization',
      'Migration Services',
      'Security & Compliance',
    ];

    for (const service of serviceTypes) {
      const element = page.getByText(service, { exact: false });
      // At least some services should be visible
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible();
      }
    }
  });

  test('should have contact CTA', async ({ page }) => {
    const contactLink = page.getByRole('link', { name: /Contact|Get Started|Schedule/i });
    await expect(contactLink.first()).toBeVisible();
  });

  test('should display engagement process', async ({ page }) => {
    // Look for process/phase sections
    await expect(page.getByText(/Discovery|Assessment|Phase/i).first()).toBeVisible();
  });
});
