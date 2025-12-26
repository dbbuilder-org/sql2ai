import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('home page should have no critical accessibility violations', async ({ page }) => {
    await page.goto('/');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    // Filter to only critical and serious violations
    const criticalViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalViolations).toHaveLength(0);
  });

  test('features page should have no critical accessibility violations', async ({ page }) => {
    await page.goto('/features');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    const criticalViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalViolations).toHaveLength(0);
  });

  test('pricing page should have no critical accessibility violations', async ({ page }) => {
    await page.goto('/pricing');

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    const criticalViolations = accessibilityScanResults.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );

    expect(criticalViolations).toHaveLength(0);
  });
});

test.describe('Keyboard Navigation', () => {
  test('should be able to navigate header with keyboard', async ({ page }) => {
    await page.goto('/');

    // Tab through the header links
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(['A', 'BUTTON']).toContain(focusedElement);
  });

  test('should be able to activate buttons with keyboard', async ({ page }) => {
    await page.goto('/');

    // Find the first button and focus it
    const button = page.getByRole('link', { name: /Start Free Trial/i }).first();
    await button.focus();

    // Press Enter to activate
    await page.keyboard.press('Enter');

    await expect(page).toHaveURL(/.*signup/);
  });
});

test.describe('Focus Management', () => {
  test('should have visible focus indicators', async ({ page }) => {
    await page.goto('/');

    // Tab to an element
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Check that there's a visible focus style
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });

  test('mobile menu should trap focus', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // Open mobile menu
    const menuButton = page.getByRole('button', { name: /Toggle menu/i });
    await menuButton.click();

    // Tab through menu items
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Focus should stay within menu
    const focusedElement = await page.evaluate(() => document.activeElement?.closest('nav'));
    expect(focusedElement).not.toBeNull();
  });
});
