const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS_DIR = 'C:/Users/athar/.gemini/antigravity-ide/brain/442628c5-fe04-4139-995b-0c55718b6889';

async function runDedicatedAnalyticsVerification() {
  console.log('=== STARTING PLAYWRIGHT VERIFICATION FOR DEDICATED WEBSITE ANALYTICS (/app/analytics) ===');

  const browser = await chromium.launch({
    channel: 'msedge',
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });

  const page = await context.newPage();

  const results = {
    authSuccess: false,
    navigatedFromCommandCenter: false,
    overviewTab: {
      rendered: false,
      brandName: '',
      websiteUrl: '',
      statusBadge: '',
      httpStatus: '',
      titleLength: '',
      pageTitle: '',
      metaDescription: '',
      headings: '',
      screenshot: ''
    },
    trafficTab: {
      rendered: false,
      truthfulStatus: '',
      headingText: '',
      connectButtonExists: false,
      screenshot: ''
    },
    searchTab: {
      rendered: false,
      truthfulStatus: '',
      headingText: '',
      connectButtonExists: false,
      screenshot: ''
    },
    consoleErrors: []
  };

  const consoleLogs = [];
  page.on('console', msg => {
    consoleLogs.push({ type: msg.type(), text: msg.text() });
    if (msg.type() === 'error') {
      console.log(`[Browser Console Error] ${msg.text()}`);
    }
  });

  try {
    // 1. Authenticate
    console.log('[Step 1] Navigating to http://localhost:3000 to authenticate...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
    
    await page.evaluate(() => {
      window.dispatchEvent(new Event('open-auth-login'));
    });

    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', 'demo@standbharat.com');
    await page.fill('input[type="password"]', 'password123');

    console.log('[Step 2] Submitting login form...');
    const loginResponsePromise = page.waitForResponse(res => res.url().includes('/api/auth/login'), { timeout: 20000 });
    await page.click('button[type="submit"]');
    const loginResponse = await loginResponsePromise;
    console.log('Login response status:', loginResponse.status());

    const cookies = await context.cookies();
    results.authSuccess = !!cookies.find(c => c.name === 'access_token');
    console.log('✓ Auth cookie set:', results.authSuccess);

    // 2. Open Command Center and click navigation link to Analytics
    console.log('[Step 2] Navigating to /app/command-center...');
    await page.goto('http://localhost:3000/app/command-center', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);

    console.log('[Step 3] Clicking top header Analytics navigation link...');
    const analyticsHeaderLink = page.locator('header a[href="/app/analytics"]').first();
    const isLinkVisible = await analyticsHeaderLink.isVisible();
    console.log('Header Analytics link visible:', isLinkVisible);

    if (isLinkVisible) {
      await analyticsHeaderLink.click();
      results.navigatedFromCommandCenter = true;
    } else {
      await page.goto('http://localhost:3000/app/analytics', { waitUntil: 'networkidle' });
    }

    await page.waitForURL('**/app/analytics', { timeout: 10000 });
    console.log('✓ Navigated to /app/analytics successfully.');
    await page.waitForTimeout(3000);

    // 3. Verify Overview Tab
    console.log('[Step 4] Verifying Overview & SEO Audit Tab...');
    const heading = await page.locator('h1').innerText();
    const brandName = await page.locator('text=Bhartiya Organic Teas').first().innerText();
    const pageTitle = await page.locator('text=Bhartiya Organic Teas | Artisanal Single-Estate Indian Teas').first().innerText();

    results.overviewTab.rendered = heading.includes('Website Analytics');
    results.overviewTab.brandName = brandName;
    results.overviewTab.pageTitle = pageTitle;

    const bodyText = await page.innerText('body');
    results.overviewTab.metaDescription = bodyText.includes('Single-origin organic Darjeeling and Assam teas') ? 'Found' : 'Missing';
    results.overviewTab.headings = bodyText.includes('1 H1 / 4 H2') ? '1 H1 / 4 H2' : 'Checked';
    results.overviewTab.httpStatus = bodyText.includes('200') ? '200 OK' : 'Unknown';

    console.log('Overview Tab verified:', {
      rendered: results.overviewTab.rendered,
      brand: results.overviewTab.brandName,
      title: results.overviewTab.pageTitle,
      metaDesc: results.overviewTab.metaDescription
    });

    const overviewScreenshot = path.join(ARTIFACTS_DIR, 'browser_analytics_overview.png');
    await page.screenshot({ path: overviewScreenshot, fullPage: true });
    results.overviewTab.screenshot = overviewScreenshot;
    console.log('✓ Saved overview screenshot:', overviewScreenshot);

    // 4. Verify Traffic Tab (GA4)
    console.log('[Step 5] Clicking Traffic Analytics (GA4) Tab...');
    const trafficTabBtn = page.locator('button:has-text("Traffic Analytics (GA4)")').first();
    await trafficTabBtn.click();
    await page.waitForTimeout(2000);

    const trafficBodyText = await page.innerText('body');
    results.trafficTab.rendered = trafficBodyText.includes('Google Analytics 4');
    results.trafficTab.truthfulStatus = trafficBodyText.includes('NOT_CONFIGURED') ? 'NOT_CONFIGURED' : (trafficBodyText.includes('NO_DATA') ? 'NO_DATA' : 'AVAILABLE');
    results.trafficTab.headingText = trafficBodyText.includes('Google Analytics 4 Not Connected') ? 'Google Analytics 4 Not Connected' : 'Connected';
    results.trafficTab.connectButtonExists = await page.locator('a[href="/app/integrations"]').first().isVisible();

    console.log('Traffic Tab verified:', {
      rendered: results.trafficTab.rendered,
      truthfulStatus: results.trafficTab.truthfulStatus,
      connectButtonExists: results.trafficTab.connectButtonExists
    });

    const trafficScreenshot = path.join(ARTIFACTS_DIR, 'browser_analytics_traffic.png');
    await page.screenshot({ path: trafficScreenshot, fullPage: true });
    results.trafficTab.screenshot = trafficScreenshot;
    console.log('✓ Saved traffic screenshot:', trafficScreenshot);

    // 5. Verify Search Performance Tab (GSC)
    console.log('[Step 6] Clicking Search Performance (GSC) Tab...');
    const searchTabBtn = page.locator('button:has-text("Search Performance (GSC)")').first();
    await searchTabBtn.click();
    await page.waitForTimeout(2000);

    const searchBodyText = await page.innerText('body');
    results.searchTab.rendered = searchBodyText.includes('Google Search Console');
    results.searchTab.truthfulStatus = searchBodyText.includes('NOT_CONFIGURED') ? 'NOT_CONFIGURED' : (searchBodyText.includes('NO_DATA') ? 'NO_DATA' : 'AVAILABLE');
    results.searchTab.headingText = searchBodyText.includes('Google Search Console Not Connected') ? 'Google Search Console Not Connected' : 'Connected';
    results.searchTab.connectButtonExists = await page.locator('a[href="/app/integrations"]').first().isVisible();

    console.log('Search Tab verified:', {
      rendered: results.searchTab.rendered,
      truthfulStatus: results.searchTab.truthfulStatus,
      connectButtonExists: results.searchTab.connectButtonExists
    });

    const searchScreenshot = path.join(ARTIFACTS_DIR, 'browser_analytics_search.png');
    await page.screenshot({ path: searchScreenshot, fullPage: true });
    results.searchTab.screenshot = searchScreenshot;
    console.log('✓ Saved search screenshot:', searchScreenshot);

    results.consoleErrors = consoleLogs.filter(l => l.type === 'error');

    fs.writeFileSync(
      path.join(ARTIFACTS_DIR, 'browser_analytics_verification.json'),
      JSON.stringify(results, null, 2)
    );
    console.log('✓ Verification summary saved to browser_analytics_verification.json');

  } catch (err) {
    console.error('Error during browser verification:', err);
    await page.screenshot({ path: path.join(ARTIFACTS_DIR, 'browser_analytics_error.png') });
    throw err;
  } finally {
    await browser.close();
    console.log('Browser closed cleanly.');
  }
}

runDedicatedAnalyticsVerification().catch(err => {
  console.error(err);
  process.exit(1);
});
