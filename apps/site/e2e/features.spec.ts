import { test, expect } from '@playwright/test';

test.describe('Features Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/features');
  });

  test('should display the features hero', async ({ page }) => {
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    await expect(page.getByText('8 Integrated Modules')).toBeVisible();
    await expect(page.getByText('Complete Database')).toBeVisible();
  });

  test('should display module navigation chips', async ({ page }) => {
    const moduleNames = ['Monitor', 'Orchestrate', 'Optimize', 'Migrate', 'Version', 'Writer', 'Comply'];

    for (const name of moduleNames) {
      await expect(page.getByRole('link', { name }).first()).toBeVisible();
    }
  });

  test('should display module cards', async ({ page }) => {
    // Check for some module cards
    await expect(page.getByText('SQL Monitor')).toBeVisible();
    await expect(page.getByText('SQL Orchestrate')).toBeVisible();
    await expect(page.getByText('SQL Optimize')).toBeVisible();
  });

  test('should navigate to individual module page', async ({ page }) => {
    await page.getByRole('link', { name: /SQL Monitor/i }).first().click();
    await expect(page).toHaveURL(/.*features\/monitor/);
  });

  test('should display database-first philosophy section', async ({ page }) => {
    await expect(page.getByText('Database-First Philosophy')).toBeVisible();
    await expect(page.getByText('Traditional Approach')).toBeVisible();
    await expect(page.getByText('SQL2.AI Approach')).toBeVisible();
  });

  test('should display integration section', async ({ page }) => {
    await expect(page.getByText('Works With Your Stack')).toBeVisible();
    await expect(page.getByText('Databases')).toBeVisible();
    await expect(page.getByText('IDEs')).toBeVisible();
  });

  test('should display compliance badges', async ({ page }) => {
    await expect(page.getByText('Enterprise Compliance Ready')).toBeVisible();
    await expect(page.getByText('SOC 2')).toBeVisible();
    await expect(page.getByText('HIPAA')).toBeVisible();
    await expect(page.getByText('PCI-DSS')).toBeVisible();
  });

  test('should have CTA section', async ({ page }) => {
    await expect(page.getByText('Ready to Transform Your Database Workflow?')).toBeVisible();
  });
});

test.describe('Individual Feature Pages', () => {
  const modulePages = [
    { path: '/features/monitor', title: 'SQL Monitor' },
    { path: '/features/orchestrate', title: 'SQL Orchestrate' },
    { path: '/features/optimize', title: 'SQL Optimize' },
    { path: '/features/migrate', title: 'SQL Migrate' },
    { path: '/features/version', title: 'SQL Version' },
    { path: '/features/code', title: 'SQL Code' },
    { path: '/features/writer', title: 'SQL Writer' },
    { path: '/features/comply', title: 'SQL Comply' },
  ];

  for (const module of modulePages) {
    test(`should load ${module.title} page`, async ({ page }) => {
      await page.goto(module.path);
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
    });
  }
});
