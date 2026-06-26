import { test, expect } from '@playwright/test';

test('home page loads with hero and navigation', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: /Improv on demand in Poland/i })).toBeVisible();
  await expect(page.getByRole('link', { name: /Browse Events/i })).toBeVisible();
  await expect(page.getByRole('link', { name: /Suggest Your City/i })).toBeVisible();
});

test('events page lists seeded workshop and jam', async ({ page }) => {
  await page.goto('/events/');

  await expect(page.getByRole('heading', { name: /^Events$/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'English Improv Workshop' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Friday Night Improv Jam' })).toBeVisible();
});

test('polls page loads with active polls', async ({ page }) => {
  await page.goto('/polls/');

  await expect(page.getByRole('heading', { name: /Crowd-powered improv map of Poland/i })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Wrocław', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Gdańsk', exact: true })).toBeVisible();
});