import { test, expect } from '@playwright/test';

test.describe('Pricing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/pricing');
  });

  test('should display pricing header', async ({ page }) => {
    await expect(page.getByText('Simple,')).toBeVisible();
    await expect(page.getByText('Transparent')).toBeVisible();
    await expect(page.getByText('Pricing')).toBeVisible();
  });

  test('should display all pricing tiers', async ({ page }) => {
    // Free tier
    await expect(page.getByText('$0')).toBeVisible();
    await expect(page.getByText('Free')).toBeVisible();

    // Professional tier
    await expect(page.getByText('$29')).toBeVisible();
    await expect(page.getByText('Professional')).toBeVisible();

    // Team tier
    await expect(page.getByText('$99')).toBeVisible();
    await expect(page.getByText('Team')).toBeVisible();
  });

  test('should highlight most popular plan', async ({ page }) => {
    await expect(page.getByText('Most Popular')).toBeVisible();
  });

  test('should display features for each tier', async ({ page }) => {
    // Free tier features
    await expect(page.getByText('1 database connection')).toBeVisible();
    await expect(page.getByText('Community support')).toBeVisible();

    // Professional tier features
    await expect(page.getByText('5 database connections')).toBeVisible();
    await expect(page.getByText('Unlimited query optimizations')).toBeVisible();

    // Team tier features
    await expect(page.getByText('Team collaboration')).toBeVisible();
    await expect(page.getByText('SSO authentication')).toBeVisible();
  });

  test('should have CTA buttons for each tier', async ({ page }) => {
    await expect(page.getByRole('link', { name: /Get Started Free/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /Start Free Trial/i }).first()).toBeVisible();
  });

  test('should display enterprise CTA', async ({ page }) => {
    await expect(page.getByText('Need Enterprise Features?')).toBeVisible();
    await expect(page.getByRole('link', { name: /Contact Sales/i })).toBeVisible();
  });
});

test.describe('Pricing Page - Interactions', () => {
  test('should navigate to signup from free tier', async ({ page }) => {
    await page.goto('/pricing');
    await page.getByRole('link', { name: /Get Started Free/i }).click();
    await expect(page).toHaveURL(/.*signup/);
  });

  test('should navigate to signup with plan for pro tier', async ({ page }) => {
    await page.goto('/pricing');
    const proButton = page.getByRole('link', { name: /Start Free Trial/i }).first();
    await proButton.click();
    await expect(page).toHaveURL(/.*signup.*plan=pro/);
  });
});
