import { test, expect } from '@playwright/test';

test('landing page loads', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page.locator('text=Your AI CMO for')).toBeVisible();
});

test('login page loads', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('text=Sign in to StandBharat')).toBeVisible();
});

test('signup page loads', async ({ page }) => {
  await page.goto('http://localhost:3000/signup');
  await expect(page.locator('text=Create your account')).toBeVisible();
});
