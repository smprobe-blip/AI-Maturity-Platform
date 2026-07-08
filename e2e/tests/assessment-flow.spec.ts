import { test, expect } from '@playwright/test';

test.describe('AI Maturity Assessment Flow', () => {
  test('complete assessment flow', async ({ page }) => {
    // Step 1: Page 1 — Company profile
    await page.goto('/');
    
    await expect(page.locator('h1')).toContainText('Оценка ИИ-зрелости');
    
    // Fill company profile
    await page.selectOption('select[name="industry"]', 'Retail');
    await page.selectOption('select[name="company_size"]', 'Large (1000+)');
    await page.selectOption('select[name="region"]', 'Moscow');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="name"]', 'John Doe');
    await page.fill('input[name="position"]', 'CTO');
    
    // Accept consent
    await page.check('input[type="checkbox"]');
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Step 2: Page 2 — Assessment
    await expect(page).toHaveURL('/assessment');
    await expect(page.locator('h2')).toContainText('Strategy & Vision');
    
    // Fill all dimensions
    for (let dim = 0; dim < 7; dim++) {
      // Fill 5 questions per dimension
      for (let q = 0; q < 5; q++) {
        const slider = page.locator('input[type="range"]').nth(q);
        await slider.fill('4');
      }
      
      // Click next (except last dimension)
      if (dim < 6) {
        await page.click('button:has-text("Далее")');
        await page.waitForTimeout(500);
      }
    }
    
    // Submit assessment
    await page.click('button:has-text("Завершить")');
    
    // Step 3: Page 3 — Results
    await expect(page).toHaveURL(/\/results\/.+/);
    
    // Check results
    await expect(page.locator('h1')).toContainText('Ваши результаты');
    await expect(page.locator('text=Комплексная оценка')).toBeVisible();
    await expect(page.locator('svg')).toBeVisible(); // Radar chart
    
    // Check dimension breakdown
    await expect(page.locator('text=Детализация по осям')).toBeVisible();
    
    // Take screenshot
    await page.screenshot({ path: 'test-results/assessment-complete.png' });
  });

  test('validation errors on Page 1', async ({ page }) => {
    await page.goto('/');
    
    // Try to submit without filling
    await page.click('button[type="submit"]');
    
    // Check validation errors
    await expect(page.locator('text=Выберите отрасль')).toBeVisible();
    await expect(page.locator('text=Некорректный email')).toBeVisible();
    await expect(page.locator('text=Необходимо согласие')).toBeVisible();
  });

  test('navigation between pages', async ({ page }) => {
    await page.goto('/');
    
    // Fill minimal data
    await page.selectOption('select[name="industry"]', 'Retail');
    await page.selectOption('select[name="company_size"]', 'Small (1-50)');
    await page.selectOption('select[name="region"]', 'Moscow');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.check('input[type="checkbox"]');
    
    // Go to assessment
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/assessment');
    
    // Go back
    await page.click('button:has-text("Назад")');
    await expect(page).toHaveURL('/');
  });
});