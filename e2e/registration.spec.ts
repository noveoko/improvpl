import { test, expect } from '@playwright/test';

test('user can register for a workshop through the modal', async ({ page }) => {
  const uniqueEmail = `e2e-${Date.now()}@example.com`;

  await page.goto('/events/');

  const workshopCard = page.locator('article').filter({ hasText: 'English Improv Workshop' });
  await workshopCard.getByRole('button', { name: 'Register' }).click();

  const modal = page.locator('[id^="register-modal-"].active');
  await expect(modal).toBeVisible();
  await expect(modal.getByText('English Improv Workshop')).toBeVisible();

  await modal.getByPlaceholder('Your name').fill('E2E Tester');
  await modal.getByPlaceholder('your@email.com').fill(uniqueEmail);
  await modal.getByRole('button', { name: 'Confirm' }).click();

  await expect(page).toHaveURL(/\/events\/$/);
  await expect(page.locator('.flash-message')).toContainText(/You're in! Check your email for confirmation/i);
});

test('home page shows featured workshop card', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'English Improv Workshop' })).toBeVisible();
  await expect(page.locator('article').filter({ hasText: 'English Improv Workshop' }).getByText('Warsaw')).toBeVisible();
});