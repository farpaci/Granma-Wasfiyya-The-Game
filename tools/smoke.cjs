// Headless smoke test: loads a built page, walks forward, screenshots, fails on JS errors.
// Usage: node tools/smoke.cjs [index.html|index_screenshot_version.html]  -> work/smoke/*.png
const path = require('path'), fs = require('fs');
const { chromium } = require('playwright');

const root = path.dirname(__dirname);
const page_ = process.argv[2] || 'index.html';
const out = path.join(root, 'work', 'smoke');
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch(fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const errors = [];
  page.on('pageerror', e => errors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !/fonts\.g/.test(m.text())) errors.push('console: ' + m.text()); });
  await page.goto('file://' + path.join(root, page_));
  await page.waitForTimeout(1500);
  const base = path.basename(page_, '.html');
  await page.screenshot({ path: path.join(out, `${base}_idle.png`) });
  await page.keyboard.down('KeyW');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(out, `${base}_walk.png`) });
  await page.keyboard.up('KeyW');
  const dist = await page.$eval('#dist span', el => el.textContent).catch(() => '?');
  await browser.close();
  console.log(`${page_}: distance after 2s walk = ${dist}; screenshots in work/smoke/`);
  if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
  console.log('OK: no JS errors');
})().catch(e => { console.error(e); process.exit(1); });
