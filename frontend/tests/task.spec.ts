import { test, expect } from '@playwright/test';

test.describe('Task', () => {

  test.beforeEach(async ({ page }) => {
    const apiUrl = process.env.API_URL || 'http://127.0.0.1:8000';
    const response = await page.request.post(`${apiUrl}/test/reset-database`);

    await test.step('Verify reset response', async () => {
      expect(response.status()).toBe(200);
    });

    await page.goto('/');
    await expect(page.locator('h1')).toContainText('Task Management');
  });

  test.describe('Task Create - Floating Button', () => {
    test('should create a new task using the create button and task form modal', async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();

      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Create New Task')).toBeVisible();

      const taskTitle = 'Test Task Title';
      const taskDescription = 'This is a test task description';

      await page.locator('input[name="title"]').fill(taskTitle);
      await page.locator('textarea[name="description"]').fill(taskDescription);

      await page.locator('button[type="submit"]').click();

      await expect(page.locator('[role="dialog"]')).not.toBeVisible();

      const taskList = page.locator('[data-testid=task-list]');

      await expect(taskList.locator(`text=${taskTitle}`)).toBeVisible();
      await expect(taskList.locator(`text=${taskDescription}`)).toBeVisible();

      const taskCard = page.locator('.border-t-gray-400').filter({ hasText: taskTitle });
      await expect(taskCard).toBeVisible();
    });
  })

  test.describe('TaskForm Modal', () => {
    test('should open and close modal correctly', async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();
      await expect(page.locator('[role="dialog"]')).toBeVisible();

      await page.keyboard.press('Escape');
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();

      await page.locator('button[aria-label="Create a new task"]').click();
      await expect(page.locator('[role="dialog"]')).toBeVisible();

      await page.locator('[role="dialog"]').press('Escape');
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();
    });

    test('should validate required fields', async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();

      await page.locator('textarea[name="description"]').fill('Description without title');
      await expect(page.locator('button[type="submit"]')).toBeDisabled();

      await expect(page.locator('[role="dialog"]')).toBeVisible();

      await page.locator('input[name="title"]').fill('Valid Title');
      await page.locator('button[type="submit"]').click();

      const taskList = page.locator('[data-testid=task-list]');
      await expect(page.locator('[role="dialog"]')).not.toBeVisible();
      await expect(taskList.locator('text=Valid Title')).toBeVisible();
    });

    test('should handle long text inputs', async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();

      const longTitle = 'A'.repeat(100);
      const longDescription = 'B'.repeat(500);

      await page.locator('input[name="title"]').fill(longTitle);
      await page.locator('textarea[name="description"]').fill(longDescription);
      await page.locator('button[type="submit"]').click();

      await expect(page.locator('[role="dialog"]')).not.toBeVisible();

      const taskCard = page.locator('.truncate').filter({ hasText: longTitle.substring(0, 20) });
      await expect(taskCard).toBeVisible();
    });
  });

  test.describe('TaskStatusBadgeDropdown', () => {
    test('should update status and reflect visual changes', async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();
      await expect(page.locator('[role="dialog"]')).toBeVisible();
      await expect(page.locator('text=Create New Task')).toBeVisible();
      await page.locator('input[name="title"]').fill('Status Test Task');
      await page.locator('textarea[name="description"]').fill('Task for status testing');
      await page.locator('button[type="submit"]').click();

      const taskCard = page.locator('text=Status Test Task').locator('..');

      await expect(page.locator('.border-t-gray-400').filter({ hasText: 'Status Test Task' })).toBeVisible();

      await taskCard.locator('[data-testid="task-card-dropdown-menu"]').click();
      await page.locator('[role="menuitem"]').filter({ hasText: 'In Progress' }).click();

      await expect(page.locator('.border-t-blue-400').filter({ hasText: 'Status Test Task' })).toBeVisible();

      await taskCard.locator('[data-testid="task-card-dropdown-menu"]').click();
      await page.locator('[role="menuitem"]').filter({ hasText: 'Done' }).click();

      await expect(page.locator('.border-t-green-400').filter({ hasText: 'Status Test Task' })).toBeVisible();
    });
  });

  test.describe('TaskCard Actions', () => {
    test.beforeEach(async ({ page }) => {
      await page.locator('button[aria-label="Create a new task"]').click();
      await page.locator('input[name="title"]').fill('Action Test Task');
      await page.locator('textarea[name="description"]').fill('Task for action testing');
      await page.locator('button[type="submit"]').click();
    });

    test('should show edit and delete options in dropdown', async ({ page }) => {
      const taskCard = page.locator('text=Action Test Task').locator('..');

      await taskCard.locator('button:has(svg)').last().click();

      await expect(page.locator('[role="menuitem"]').filter({ hasText: 'Edit' })).toBeVisible();
      await expect(page.locator('[role="menuitem"]').filter({ hasText: 'Delete' })).toBeVisible();
    });

    test('should populate edit form with existing data', async ({ page }) => {
      const taskCard = page.locator('text=Action Test Task').locator('..');

      await taskCard.locator('button:has(svg)').last().click();
      await page.locator('[role="menuitem"]').filter({ hasText: 'Edit' }).click();

      await expect(page.locator('input[name="title"]')).toHaveValue('Action Test Task');
      await expect(page.locator('textarea[name="description"]')).toHaveValue('Task for action testing');

      await expect(page.locator('text=Edit Task')).toBeVisible();
    });

    test('should handle edit cancellation', async ({ page }) => {
      const taskCard = page.locator('text=Action Test Task').locator('..');

      await taskCard.locator('button:has(svg)').last().click();
      await page.locator('[role="menuitem"]').filter({ hasText: 'Edit' }).click();

      await page.locator('input[name="title"]').fill('Modified Title');

      await page.locator('button', { hasText: 'Cancel' }).click();

      const taskList = page.locator('[data-testid=task-list]');
      await expect(taskList.locator('text=Action Test Task')).toBeVisible();
      await expect(taskList.locator('text=Modified Title')).not.toBeVisible();
    });

    test('should confirm delete action', async ({ page }) => {
      const taskCard = page.locator('text=Action Test Task').locator('..');

      await taskCard.locator('button:has(svg)').last().click();
      await page.locator('[role="menuitem"]').filter({ hasText: 'Delete' }).click();
      await page.locator('[data-testid="confirm-delete-button"]').click();

      const taskList = page.locator('[data-testid=task-list]');
      await expect(taskList.locator('text=Action Test Task')).not.toBeVisible();
    });
  });
});