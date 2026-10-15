// @ts-check
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://eqms.doe.gov.my/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/MyEQMS/);
});

test('APIMS link', async ({ page }) => {
  await page.goto('https://eqms.doe.gov.my/APIMS/main/');

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByText('Air Pollutant Index Management System (APIMS)'));

  // Filter Selangor. 
  await page.getByRole('button', { name: 'Filter' }).nth(1).click();
  await expect(page.getByText('Filter Listing'));
  await page.getByRole('radio', { name: 'Selangor' }).click();
  await page.getByRole('button', { name: 'GENERATE' }).click(); 

  // Get reading. 
  const rows = await page.locator('table tbody tr').all(); 
  for (const row of rows) {
    // Get text from all cells in the row as an array. 
    const rowData = await row.locator('td').allTextContents(); 
    console.log('Row text data: ', rowData); 

    // Iterate through each cell. 
    const cells = await row.locator('td').all(); 
    for (const cell of cells) {
      //const text = await cell.innerText(); 
      //console.log('Cell content: ', text);
    }
  }
});