const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS_DIR = 'C:/Users/athar/.gemini/antigravity-ide/brain/442628c5-fe04-4139-995b-0c55718b6889';

async function runLiveVerification() {
  console.log('--- STARTING PLAYWRIGHT BROWSER VERIFICATION (MSEDGE) ---');
  
  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });

  const page = await context.newPage();

  const networkLogs = [];
  const consoleLogs = [];
  const errors = [];

  page.on('console', msg => {
    consoleLogs.push({ type: msg.type(), text: msg.text() });
  });

  page.on('pageerror', err => {
    errors.push(err.toString());
    console.error('Page Error:', err);
  });

  page.on('request', req => {
    if (req.url().includes('/api/')) {
      networkLogs.push({
        event: 'request',
        url: req.url(),
        method: req.method(),
        headers: req.headers()
      });
    }
  });

  page.on('response', async res => {
    if (res.url().includes('/api/')) {
      networkLogs.push({
        event: 'response',
        url: res.url(),
        status: res.status(),
        statusText: res.statusText()
      });
    }
  });

  const results = {
    authCookieSet: false,
    brandSelected: false,
    brandName: '',
    strategyFields: {},
    documentsVerified: {},
    consoleErrors: [],
    networkSummary: []
  };

  try {
    // 1. Navigate to Landing / Login
    console.log('[Step 1] Navigating to http://localhost:3000...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Open Login Modal
    console.log('[Step 2] Opening login modal via window event...');
    await page.evaluate(() => {
      window.dispatchEvent(new Event('open-auth-login'));
    });

    // Wait for email input
    console.log('[Step 3] Waiting for login form inputs...');
    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    
    await page.fill('input[type="email"]', 'demo@standbharat.com');
    await page.fill('input[type="password"]', 'password123');
    
    console.log('[Step 4] Submitting login form...');
    // Click submit
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForResponse(res => res.url().includes('/api/auth/login') && res.status() === 200, { timeout: 15000 })
    ]);

    console.log('[Step 5] Login successful. Checking cookies...');
    const cookies = await context.cookies();
    const tokenCookie = cookies.find(c => c.name === 'access_token');
    results.authCookieSet = !!tokenCookie;
    console.log('Auth cookie present:', results.authCookieSet, tokenCookie ? `(HttpOnly=${tokenCookie.httpOnly}, Path=${tokenCookie.path})` : '');

    // Wait for navigation or navigate to /app/command-center
    console.log('[Step 6] Navigating to /app/command-center...');
    await page.goto('http://localhost:3000/app/command-center', { waitUntil: 'networkidle', timeout: 30000 });
    
    // Allow provider effects to hydrate
    await page.waitForTimeout(3000);

    // Verify Brand Selection
    const brandElement = await page.locator('text=Bhartiya Organic Teas').first();
    if (await brandElement.isVisible()) {
      results.brandSelected = true;
      results.brandName = 'Bhartiya Organic Teas';
      console.log('Verified active brand visible in DOM: Bhartiya Organic Teas');
    } else {
      console.log('Brand text not immediately found, querying workspace card text...');
      const cardText = await page.locator('.truncate').allInnerTexts();
      console.log('Truncate texts:', cardText);
    }

    // 2. Verify Strategy Panel
    console.log('[Step 7] Clicking Strategy nav tab...');
    const strategyTab = page.locator('text="Strategy"').first();
    await strategyTab.click();
    await page.waitForTimeout(2000);

    // Wait for textarea business_strategy
    console.log('[Step 8] Checking BrandStrategy textareas...');
    await page.waitForSelector('textarea[name="business_strategy"]', { timeout: 10000 });

    const strategyNames = [
      'business_strategy',
      'marketing_strategy',
      'content_strategy',
      'channel_strategy',
      'growth_strategy',
      'campaign_strategy'
    ];

    for (const name of strategyNames) {
      const val = await page.inputValue(`textarea[name="${name}"]`);
      results.strategyFields[name] = {
        length: val.length,
        preview: val.substring(0, 80) + '...'
      };
      console.log(`  - ${name}: [${val.length} chars] ${val.substring(0, 80)}...`);
    }

    const stratScreenshotPath = path.join(ARTIFACTS_DIR, 'browser_strategy_panel.png');
    await page.screenshot({ path: stratScreenshotPath });
    console.log('Saved screenshot:', stratScreenshotPath);

    // 3. Verify Foundational Documents
    const docTabs = [
      { tab: 'Product Information', expectedType: 'PRODUCT_INFORMATION' },
      { tab: 'Competitor Analysis', expectedType: 'COMPETITOR_ANALYSIS' },
      { tab: 'Brand Voice Guide', expectedType: 'BRAND_VOICE' },
      { tab: 'Growth Playbook', expectedType: 'GROWTH_PLAYBOOK' }
    ];

    for (const doc of docTabs) {
      console.log(`[Step 9] Clicking Knowledge Base tab: "${doc.tab}"...`);
      const docNav = page.locator(`text="${doc.tab}"`).first();
      await docNav.click();
      await page.waitForTimeout(2000);

      // Verify content
      const heading = await page.locator('h2.text-\\[18px\\]').first().innerText();
      const summaryLocator = page.locator('div.max-w-3xl p').first();
      const hasSummary = await summaryLocator.isVisible();
      const summary = hasSummary ? await summaryLocator.innerText() : '';
      const sectionHeadings = await page.locator('div.max-w-3xl h3').allInnerTexts();

      results.documentsVerified[doc.tab] = {
        heading,
        hasSummary,
        summaryPreview: summary.substring(0, 80) + '...',
        sectionCount: sectionHeadings.length,
        sections: sectionHeadings
      };

      console.log(`  Document: "${doc.tab}"`);
      console.log(`    Heading: ${heading}`);
      console.log(`    Sections (${sectionHeadings.length}): ${sectionHeadings.join(', ')}`);

      const docScreenshotPath = path.join(ARTIFACTS_DIR, `browser_${doc.expectedType.toLowerCase()}.png`);
      await page.screenshot({ path: docScreenshotPath });
      console.log('    Saved screenshot:', docScreenshotPath);
    }

    results.consoleErrors = consoleLogs.filter(l => l.type === 'error');
    results.pageErrors = errors;
    results.networkSummary = networkLogs;

    console.log('\n--- BROWSER VERIFICATION SUMMARY ---');
    console.log('Auth Cookie Set:', results.authCookieSet);
    console.log('Brand Selected:', results.brandSelected, `(${results.brandName})`);
    console.log('Strategy Fields Loaded:', Object.keys(results.strategyFields).length);
    console.log('Foundational Documents Verified:', Object.keys(results.documentsVerified).length);
    console.log('Console Errors:', results.consoleErrors.length);
    console.log('Page Errors:', results.pageErrors.length);

    fs.writeFileSync(
      path.join(ARTIFACTS_DIR, 'browser_verification_results.json'),
      JSON.stringify(results, null, 2)
    );
    console.log('Results written to browser_verification_results.json');

  } catch (err) {
    console.error('Browser verification failed with error:', err);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'browser_error_screenshot.png') });
    throw err;
  } finally {
    await browser.close();
    console.log('Browser closed cleanly.');
  }
}

runLiveVerification().catch(err => {
  console.error(err);
  process.exit(1);
});
