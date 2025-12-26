import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the hero section', async ({ page }) => {
    // Check main headline
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('Database Development')).toBeVisible();
    await expect(page.getByText('Powered by AI')).toBeVisible();
  });

  test('should display the announcement badge', async ({ page }) => {
    await expect(page.getByText('Now with Claude MCP Integration')).toBeVisible();
  });

  test('should have CTA buttons', async ({ page }) => {
    const startTrialBtn = page.getByRole('link', { name: /Start Free Trial/i });
    const watchDemoBtn = page.getByRole('link', { name: /Watch Demo/i });

    await expect(startTrialBtn).toBeVisible();
    await expect(watchDemoBtn).toBeVisible();
  });

  test('should display platform badges', async ({ page }) => {
    await expect(page.getByText('PostgreSQL')).toBeVisible();
    await expect(page.getByText('SQL Server')).toBeVisible();
    await expect(page.getByText('Azure SQL')).toBeVisible();
  });

  test('should display stats', async ({ page }) => {
    await expect(page.getByText('26+')).toBeVisible();
    await expect(page.getByText('AI Modules')).toBeVisible();
    await expect(page.getByText('10x')).toBeVisible();
    await expect(page.getByText('Faster Development')).toBeVisible();
  });

  test('should navigate to features page', async ({ page }) => {
    await page.getByRole('link', { name: /Features/i }).first().click();
    await expect(page).toHaveURL(/.*features/);
  });

  test('should navigate to pricing page', async ({ page }) => {
    await page.getByRole('link', { name: /Pricing/i }).first().click();
    await expect(page).toHaveURL(/.*pricing/);
  });

  test('should have working navigation', async ({ page }) => {
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();

    const navLinks = ['Features', 'Consulting', 'Pricing', 'Docs', 'Blog'];
    for (const link of navLinks) {
      await expect(page.getByRole('link', { name: link }).first()).toBeVisible();
    }
  });

  test('should have login and signup links', async ({ page }) => {
    await expect(page.getByRole('link', { name: /Log in/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Start Free/i })).toBeVisible();
  });
});

test.describe('Home Page - Mobile', () => {
  test.use({ viewport: { width: 375, height: 667 } });

  test('should display mobile menu button', async ({ page }) => {
    await page.goto('/');
    const menuButton = page.getByRole('button', { name: /Toggle menu/i });
    await expect(menuButton).toBeVisible();
  });

  test('should open mobile menu', async ({ page }) => {
    await page.goto('/');
    const menuButton = page.getByRole('button', { name: /Toggle menu/i });
    await menuButton.click();

    // Check mobile navigation is visible
    await expect(page.getByRole('link', { name: 'Features' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Pricing' })).toBeVisible();
  });
});

test.describe('Home Page - Scroll Behavior', () => {
  test('should show header background on scroll', async ({ page }) => {
    await page.goto('/');

    // Initially header should be transparent
    const header = page.locator('header');

    // Scroll down
    await page.evaluate(() => window.scrollTo(0, 100));
    await page.waitForTimeout(500);

    // Header should have background after scroll
    await expect(header).toHaveClass(/backdrop-blur/);
  });
});
