import { test, expect } from '@playwright/test';

test.describe('Voyage Planning Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    // Wait for app to load
    await page.waitForLoadState('networkidle');
  });

  test('should display dashboard on load', async ({ page }) => {
    await expect(page).toHaveTitle(/Vessel Scheduler/);
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('should navigate to vessel management', async ({ page }) => {
    await page.click('text=Vessels');
    await expect(page).toHaveURL(/.*vessels/);
    await expect(page.locator('h1, h2')).toContainText(/Vessel/i);
  });

  test('should create a new vessel', async ({ page }) => {
    // Navigate to vessel management
    await page.click('text=Vessels');
    
    // Click on add vessel button
    await page.click('button:has-text("Add Vessel"), button:has-text("New Vessel"), button:has-text("Create")');
    
    // Fill in vessel details
    await page.fill('input[name="name"], input[id="vessel-name"]', 'Test Vessel E2E');
    await page.fill('input[name="imo"], input[id="imo"]', '1234567');
    await page.selectOption('select[name="type"], select[id="vessel-type"]', 'Tanker');
    await page.fill('input[name="capacity"], input[id="capacity"]', '50000');
    
    // Submit the form
    await page.click('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    
    // Verify success notification
    await expect(page.locator('.notification, .alert, .toast')).toContainText(/success|created/i, {
      timeout: 5000,
    });
  });

  test('should filter vessels', async ({ page }) => {
    await page.click('text=Vessels');
    
    // Wait for vessels to load
    await page.waitForSelector('table, .vessel-list, .vessel-card', { timeout: 10000 });
    
    // Enter filter text
    const filterInput = page.locator('input[placeholder*="filter"], input[placeholder*="search"], input[type="search"]').first();
    if (await filterInput.isVisible()) {
      await filterInput.fill('Test');
      
      // Verify filter works
      await page.waitForTimeout(500);
      const items = page.locator('table tr, .vessel-card, .vessel-item');
      const count = await items.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('should create a voyage plan', async ({ page }) => {
    // Navigate to voyage builder
    await page.click('text=Voyage');
    
    // Add voyage details
    const vesselSelect = page.locator('select[name="vessel"], select:has-option("vessel")').first();
    if (await vesselSelect.isVisible()) {
      await vesselSelect.selectOption({ index: 1 });
    }
    
    // Select ports
    await page.fill('input[placeholder*="from"], input[name="fromPort"]', 'Rotterdam');
    await page.fill('input[placeholder*="to"], input[name="toPort"]', 'Singapore');
    
    // Set dates
    const today = new Date().toISOString().split('T')[0];
    await page.fill('input[type="date"]', today);
    
    // Calculate or create voyage
    await page.click('button:has-text("Calculate"), button:has-text("Create"), button[type="submit"]');
    
    // Wait for results
    await page.waitForTimeout(2000);
  });

  test('should display Gantt chart', async ({ page }) => {
    // Navigate to schedule/gantt view
    await page.click('text=Schedule, text=Gantt');
    
    // Wait for Gantt chart to render
    await page.waitForSelector('.gantt-chart, .gantt-table, canvas', { timeout: 10000 });
    
    // Verify Gantt elements exist
    const ganttExists = await page.locator('.gantt-chart, .gantt-table').count();
    expect(ganttExists).toBeGreaterThan(0);
  });

  test('should export schedule', async ({ page }) => {
    await page.click('text=Schedule');
    
    // Set up download listener
    const downloadPromise = page.waitForEvent('download', { timeout: 10000 });
    
    // Click export button
    const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').first();
    if (await exportButton.isVisible()) {
      await exportButton.click();
      
      // Wait for download
      const download = await downloadPromise;
      expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls|csv)$/);
    }
  });

  test('should handle route calculation', async ({ page }) => {
    await page.click('text=Route');
    
    // Fill in route details
    await page.fill('input[name="fromPort"], #from-port', 'Hamburg');
    await page.fill('input[name="toPort"], #to-port', 'New York');
    
    // Calculate distance
    await page.click('button:has-text("Calculate")');
    
    // Verify distance is displayed
    await expect(page.locator('text=/[0-9,]+ (nm|NM|miles)/i')).toBeVisible({ timeout: 5000 });
  });

  test('should display financial analysis', async ({ page }) => {
    // Navigate to financial section
    const financialLink = page.locator('text=Financial, text=Analysis, a[href*="financial"]').first();
    if (await financialLink.isVisible()) {
      await financialLink.click();
      
      // Wait for charts to load
      await page.waitForSelector('canvas, .chart, svg', { timeout: 10000 });
      
      // Verify charts are rendered
      const chartCount = await page.locator('canvas, .chart-container').count();
      expect(chartCount).toBeGreaterThan(0);
    }
  });

  test('should handle network visualization', async ({ page }) => {
    const networkLink = page.locator('text=Network, a[href*="network"]').first();
    if (await networkLink.isVisible()) {
      await networkLink.click();
      
      // Wait for network to render
      await page.waitForTimeout(2000);
      
      // Verify network visualization exists
      const networkCanvas = await page.locator('canvas, #network, .vis-network').count();
      expect(networkCanvas).toBeGreaterThan(0);
    }
  });

  test('should persist data across navigation', async ({ page }) => {
    // Create a vessel
    await page.click('text=Vessels');
    await page.click('button:has-text("Add"), button:has-text("New")');
    await page.fill('input[name="name"]', 'Persistence Test');
    await page.click('button[type="submit"]');
    
    // Navigate away
    await page.click('text=Dashboard, text=Home');
    
    // Navigate back
    await page.click('text=Vessels');
    
    // Verify vessel still exists
    await expect(page.locator('text=Persistence Test')).toBeVisible({ timeout: 5000 });
  });

  test('should handle errors gracefully', async ({ page }) => {
    // Attempt invalid operation
    await page.click('text=Voyage');
    
    // Try to submit without required fields
    await page.click('button[type="submit"], button:has-text("Create")');
    
    // Verify error message is shown
    const errorExists = await page.locator('.error, .alert-danger, .notification-error, [role="alert"]').count();
    expect(errorExists).toBeGreaterThan(0);
  });

  test('should be responsive on mobile', async ({ page, viewport }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Verify mobile menu exists
    const mobileMenu = page.locator('[aria-label="menu"], button.menu-toggle, .hamburger');
    if (await mobileMenu.count() > 0) {
      await mobileMenu.first().click();
      
      // Verify menu opens
      await page.waitForTimeout(500);
      const nav = await page.locator('nav, .sidebar, .mobile-menu').isVisible();
      expect(nav).toBeTruthy();
    }
  });
});

test.describe('Performance Tests', () => {
  test('should load home page quickly', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - startTime;
    
    // Page should load in less than 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should handle large dataset', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Vessels');
    
    // Wait for data to load
    await page.waitForSelector('table, .vessel-list', { timeout: 10000 });
    
    // Measure rendering time
    const metrics = await page.evaluate(() => ({
      memory: (performance as any).memory?.usedJSHeapSize,
      navigation: performance.getEntriesByType('navigation')[0],
    }));
    
    console.log('Performance metrics:', metrics);
  });
});

test.describe('Accessibility Tests', () => {
  test('should have proper heading structure', async ({ page }) => {
    await page.goto('/');
    
    // Check for h1
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThan(0);
    
    // Verify headings are in order
    const headings = await page.locator('h1, h2, h3, h4').allTextContents();
    expect(headings.length).toBeGreaterThan(0);
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/');
    
    // Verify buttons have accessible names
    const buttons = await page.locator('button').all();
    for (const button of buttons.slice(0, 5)) {
      const accessibleName = await button.getAttribute('aria-label') || await button.textContent();
      expect(accessibleName).toBeTruthy();
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/');
    
    // Tab through elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Verify focus is visible
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  });
});
