// Records a short product tour of the production-style stack as a webm (scripts/demo/record.sh turns it into a 30 fps mp4).
import { chromium } from 'playwright-core';

const BASE = process.env.BASE_URL ?? 'http://host.docker.internal:8011';
const OUT = process.env.OUT_DIR ?? '/out';
const pause = (ms) => new Promise((r) => setTimeout(r, ms));

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
  recordVideo: { dir: OUT, size: { width: 1280, height: 800 } },
  colorScheme: 'light',
});
const page = await context.newPage();

async function glide(locator, ms = 700) {
  const box = await locator.boundingBox();
  if (!box) return;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 28 });
  await pause(ms);
}

await page.goto(`${BASE}/login`, { waitUntil: 'networkidle' });
await pause(900);
await page.locator('input[type=email]').click();
await page.keyboard.type('demo@kudos.test', { delay: 45 });
await page.locator('input[type=password]').click();
await page.keyboard.type('password', { delay: 45 });
await pause(300);
await page.keyboard.press('Enter');
await page.waitForURL('**/dashboard');
await pause(1400);

for (const card of await page.locator('main .lift').all()) await glide(card, 450);
await pause(500);

await glide(page.getByRole('link', { name: 'Spaces' }).first(), 400);
await page.getByRole('link', { name: 'Spaces' }).first().click();
await page.waitForURL('**/spaces');
await pause(1100);
await glide(page.locator('main .lift').first(), 900);

await page.getByRole('link', { name: /Open inbox/ }).first().click();
await page.waitForLoadState('networkidle');
await pause(1000);
await page.mouse.wheel(0, 520);
await pause(900);
for (const card of (await page.locator('main .lift').all()).slice(0, 3)) await glide(card, 500);
await page.mouse.wheel(0, -900);
await pause(600);

await page.getByRole('link', { name: 'Edit' }).first().click();
await page.waitForLoadState('networkidle');
await pause(900);
const name = page.locator('input').first();
await name.click();
await pause(900);
await page.keyboard.press('End');
await page.keyboard.type(' 2026', { delay: 70 });
await pause(1200);
await page.locator('textarea').first().click();
await pause(1200);

await glide(page.getByRole('button', { name: /collapse|toggle sidebar/i }).first(), 300).catch(() => {});
await page.keyboard.press('Control+b');
await pause(1100);
await page.keyboard.press('Control+b');
await pause(900);

await page.getByRole('radio', { name: 'Dark' }).last().scrollIntoViewIfNeeded();
await page.getByRole('radio', { name: 'Dark' }).last().click();
await pause(1500);
await page.getByRole('link', { name: 'Dashboard' }).first().click();
await page.waitForURL('**/dashboard');
await pause(1200);
for (const card of await page.locator('main .lift').all()) await glide(card, 400);
await pause(900);

await context.close();
await browser.close();
