import { test, expect, type Page } from '@playwright/test';

const SETTINGS = {
  min_notice_days: 0,
  allow_pay_on_day: true,
  min_booking_hours: 1,
  min_cancellation_notice_days: 1,
};

function futureDateISO(): string {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toLocaleDateString('en-CA');
}

function makeAvailability(date: string) {
  return {
    is_open: true,
    date,
    open_time: '10:00',
    close_time: '23:00',
    min_booking_hours: 1,
    rooms: [{
      room_id: 1,
      name: 'Room 101',
      slug: 'room-101',
      hourly_rate: '11.69',
      slots: [
        { start_time: `${date}T10:00:00+00:00`, max_hours: 13 },
        { start_time: `${date}T11:00:00+00:00`, max_hours: 12 },
      ],
    }],
  };
}

async function mockApi(page: Page): Promise<string> {
  const testDate = futureDateISO();
  await page.route(/\/api\/settings\//, route => route.fulfill({ json: SETTINGS }));
  await page.route(/\/api\/availability\//, route => route.fulfill({ json: makeAvailability(testDate) }));
  return testDate;
}

async function waitForStep(page: Page, name: string): Promise<void> {
  await expect(page.locator('.progress-step.active')).toHaveText(name, { timeout: 8000 });
}

async function advanceToRoom(page: Page, testDate: string): Promise<void> {
  await page.locator('input[type="date"]').fill(testDate);
  await page.getByRole('button', { name: /check availability/i }).click();
  await waitForStep(page, 'Room');
}

test('back from Room → returns to Date, stays on /book', async ({ page }) => {
  const testDate = await mockApi(page);
  await page.goto('/book');
  await waitForStep(page, 'Date');

  await advanceToRoom(page, testDate);

  await page.goBack();
  await expect(page).toHaveURL(/\/book/);
  await waitForStep(page, 'Date');
});

test('back from Slot → returns to Room, stays on /book', async ({ page }) => {
  const testDate = await mockApi(page);
  await page.goto('/book');
  await waitForStep(page, 'Date');

  await advanceToRoom(page, testDate);
  await page.locator('button.room-card').first().click();
  await waitForStep(page, 'Time');

  await page.goBack();
  await expect(page).toHaveURL(/\/book/);
  await waitForStep(page, 'Room');
});

test('back from Date step navigates away from /book', async ({ page }) => {
  await mockApi(page);
  await page.goto('/');
  await page.goto('/book');
  await waitForStep(page, 'Date');

  await page.goBack();
  await expect(page).not.toHaveURL(/\/book/);
});

test('beforeunload fires when navigating away mid-flow', async ({ page }) => {
  const testDate = await mockApi(page);
  await page.goto('/book');
  await waitForStep(page, 'Date');

  await advanceToRoom(page, testDate);

  let dialogFired = false;
  page.once('dialog', async dialog => {
    dialogFired = true;
    await dialog.dismiss();
  });

  page.evaluate(() => { window.location.href = '/'; }).catch(() => {});
  await page.waitForTimeout(1500);

  expect(dialogFired).toBe(true);
});
