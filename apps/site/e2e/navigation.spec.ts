import { test, expect } from '@playwright/test';

test.describe('Site Navigation', () => {
  test('should have consistent header across pages', async ({ page }) => {
    const pages = ['/', '/features', '/pricing', '/consulting', '/docs', '/blog'];

    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator('header')).toBeVisible();
      await expect(page.getByRole('link', { name: /SQL2\.AI/i })).toBeVisible();
    }
  });

  test('should have consistent footer across pages', async ({ page }) => {
    const pages = ['/', '/features', '/pricing'];

    for (const url of pages) {
      await page.goto(url);
      await expect(page.locator('footer')).toBeVisible();
    }
  });

  test('logo should navigate to home', async ({ page }) => {
    await page.goto('/features');
    await page.getByRole('link', { name: /SQL2\.AI/i }).first().click();
    await expect(page).toHaveURL('/');
  });

  test('should have working breadcrumb on feature pages', async ({ page }) => {
    await page.goto('/features/monitor');

    // Navigate back to features
    const featuresLink = page.getByRole('link', { name: 'Features' });
    if (await featuresLink.count() > 0) {
      await featuresLink.first().click();
      await expect(page).toHaveURL(/.*features/);
    }
  });
});

test.describe('404 Page', () => {
  test('should display 404 for non-existent pages', async ({ page }) => {
    await page.goto('/non-existent-page-12345');
    await expect(page.getByText(/404|not found/i)).toBeVisible();
  });

  test('should have link back to home', async ({ page }) => {
    await page.goto('/non-existent-page-12345');
    const homeLink = page.getByRole('link', { name: /home|back/i });
    if (await homeLink.count() > 0) {
      await homeLink.first().click();
      await expect(page).toHaveURL('/');
    }
  });
});

test.describe('External Links', () => {
  test('should open docs links correctly', async ({ page }) => {
    await page.goto('/');
    const docsLink = page.getByRole('link', { name: 'Docs' }).first();
    await docsLink.click();
    await expect(page).toHaveURL(/.*docs/);
  });

  test('should open blog links correctly', async ({ page }) => {
    await page.goto('/');
    const blogLink = page.getByRole('link', { name: 'Blog' }).first();
    await blogLink.click();
    await expect(page).toHaveURL(/.*blog/);
  });
});
