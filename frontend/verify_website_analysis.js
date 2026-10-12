const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const ARTIFACTS_DIR = 'C:/Users/athar/.gemini/antigravity-ide/brain/442628c5-fe04-4139-995b-0c55718b6889';

async function runWebsiteAnalysisVerification() {
  console.log('=== STARTING PLAYWRIGHT BROWSER VERIFICATION FOR WEBSITE ANALYSIS ===');
  
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
    if (msg.type() === 'error') {
      console.log(`[Browser Console Error] ${msg.text()}`);
    }
  });

  page.on('pageerror', err => {
    errors.push(err.toString());
    console.error('[Browser Page Error]', err);
  });

  page.on('response', async res => {
    if (res.url().includes('/api/')) {
      networkLogs.push({
        url: res.url(),
        status: res.status(),
        statusText: res.statusText()
      });
    }
  });

  const verificationResult = {
    authSuccess: false,
    commandCenter: {
      url: '/app/command-center',
      sidebarClicked: false,
      panelRendered: false,
      statusDisplayed: '',
      extractedSignals: {},
      screenshot: ''
    },
    appRoot: {
      url: '/app',
      sidebarClicked: false,
      panelRendered: false,
      statusDisplayed: '',
      screenshot: ''
    },
    consoleErrors: [],
    pageErrors: []
  };

  try {
    // Step 1: Login
    console.log('[Step 1] Navigating to http://localhost:3000 to authenticate...');
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
    
    await page.evaluate(() => {
      window.dispatchEvent(new Event('open-auth-login'));
    });

    await page.waitForSelector('input[type="email"]', { timeout: 10000 });
    await page.fill('input[type="email"]', 'demo@standbharat.com');
    await page.fill('input[type="password"]', 'password123');

    console.log('[Step 2] Submitting login form...');
    await Promise.all([
      page.click('button[type="submit"]'),
      page.waitForResponse(res => res.url().includes('/api/auth/login') && res.status() === 200, { timeout: 15000 })
    ]);

    const cookies = await context.cookies();
    const tokenCookie = cookies.find(c => c.name === 'access_token');
    verificationResult.authSuccess = !!tokenCookie;
    console.log('✓ Auth cookie set:', verificationResult.authSuccess);

    // Step 2: Command Center verification
    console.log('[Step 3] Navigating to /app/command-center...');
    await page.goto('http://localhost:3000/app/command-center', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    // Check brand selection
    const brandHeading = await page.locator('text=Bhartiya Organic Teas').first();
    const isBrandVisible = await brandHeading.isVisible();
    console.log('Brand visible in header:', isBrandVisible);

    // Find and click "Website Analysis" in sidebar
    console.log('[Step 4] Locating "Website Analysis" sidebar item...');
    const websiteAnalysisNavItem = page.locator('div:has-text("Website Analysis")').filter({ hasText: /^Website Analysis$/ }).first();
    const sidebarExists = await websiteAnalysisNavItem.isVisible();
    console.log('Website Analysis sidebar item visible:', sidebarExists);

    if (sidebarExists) {
      await websiteAnalysisNavItem.click();
    } else {
      // Fallback selector for the sidebar div
      const sidebarItem = page.locator('span:text-is("Website Analysis")').first();
      await sidebarItem.click();
    }
    verificationResult.commandCenter.sidebarClicked = true;
    console.log('✓ Clicked Website Analysis sidebar navigation item.');

    // Wait for WebsiteAnalysisPanel to render and fetch data
    await page.waitForTimeout(3000);

    // Check panel elements
    const extractedSignalsHeader = page.locator('text="Extracted Signals"').first();
    const panelHeader = page.locator('div:text-is("Website Analysis")').first();
    const isSignalsHeaderVisible = await extractedSignalsHeader.isVisible();
    const isPanelHeaderVisible = await panelHeader.isVisible();

    verificationResult.commandCenter.panelRendered = isSignalsHeaderVisible || isPanelHeaderVisible;
    console.log('✓ WebsiteAnalysisPanel rendered in DOM:', verificationResult.commandCenter.panelRendered);

    // Read signals from DOM
    if (isSignalsHeaderVisible) {
      const pageText = await page.innerText('body');
      const hasFinalUrl = pageText.includes('bhartiyatea.example.com');
      const hasTitle = pageText.includes('Bhartiya Organic Teas | Artisanal Single-Estate Indian Teas');
      const hasMetaDesc = pageText.includes('Single-origin organic Darjeeling and Assam teas');
      const hasH1 = pageText.includes('H1 Tag(s)');
      const hasH2 = pageText.includes('H2 Tag(s)');
      const hasCanonical = pageText.includes('Canonical Tag');
      const hasRobots = pageText.includes('robots.txt');
      const hasSitemap = pageText.includes('sitemap.xml');
      const hasWordCount = pageText.includes('Words');
      const hasImages = pageText.includes('Total');

      verificationResult.commandCenter.extractedSignals = {
        hasFinalUrl,
        hasTitle,
        hasMetaDesc,
        hasH1,
        hasH2,
        hasCanonical,
        hasRobots,
        hasSitemap,
        hasWordCount,
        hasImages
      };

      console.log('Extracted Signals DOM verification:', verificationResult.commandCenter.extractedSignals);
    }

    const ccScreenshotPath = path.join(ARTIFACTS_DIR, 'browser_website_analysis_command_center.png');
    await page.screenshot({ path: ccScreenshotPath, fullPage: true });
    verificationResult.commandCenter.screenshot = ccScreenshotPath;
    console.log('✓ Saved screenshot to:', ccScreenshotPath);

    // Step 3: Test Synchronized /app route
    console.log('[Step 5] Navigating to synchronized /app route...');
    await page.goto('http://localhost:3000/app', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);

    const appSidebarItem = page.locator('span:text-is("Website Analysis")').first();
    await appSidebarItem.click();
    verificationResult.appRoot.sidebarClicked = true;
    console.log('✓ Clicked Website Analysis sidebar item in /app.');

    await page.waitForTimeout(3000);
    const appSignalsHeader = page.locator('text="Extracted Signals"').first();
    verificationResult.appRoot.panelRendered = await appSignalsHeader.isVisible();
    console.log('✓ WebsiteAnalysisPanel rendered in /app:', verificationResult.appRoot.panelRendered);

    const appScreenshotPath = path.join(ARTIFACTS_DIR, 'browser_website_analysis_app.png');
    await page.screenshot({ path: appScreenshotPath, fullPage: true });
    verificationResult.appRoot.screenshot = appScreenshotPath;
    console.log('✓ Saved screenshot to:', appScreenshotPath);

    verificationResult.consoleErrors = consoleLogs.filter(l => l.type === 'error');
    verificationResult.pageErrors = errors;

    fs.writeFileSync(
      path.join(ARTIFACTS_DIR, 'browser_website_analysis_verification.json'),
      JSON.stringify(verificationResult, null, 2)
    );
    console.log('✓ Saved verification results to browser_website_analysis_verification.json');

    console.log('\n=== BROWSER VERIFICATION SUMMARY ===');
    console.log('Auth Cookie Set:', verificationResult.authSuccess);
    console.log('/app/command-center Panel Rendered:', verificationResult.commandCenter.panelRendered);
    console.log('/app Panel Rendered:', verificationResult.appRoot.panelRendered);
    console.log('SEO Signals Present in DOM:', Object.values(verificationResult.commandCenter.extractedSignals).every(v => v === true));
    console.log('Console Errors:', verificationResult.consoleErrors.length);
    console.log('Page Errors:', verificationResult.pageErrors.length);

  } catch (error) {
    console.error('Browser verification failed with error:', error);
    const errScreenshotPath = path.join(ARTIFACTS_DIR, 'browser_website_analysis_error.png');
    await page.screenshot({ path: errScreenshotPath });
    throw error;
  } finally {
    await browser.close();
    console.log('Browser closed cleanly.');
  }
}

runWebsiteAnalysisVerification().catch(err => {
  console.error(err);
  process.exit(1);
});
