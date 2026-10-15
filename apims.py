import datetime
import re
import numpy as np 
import pandas as pd 

import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
	# Launch a browser. 
	chromium = playwright.chromium
	browser = await chromium.launch(headless=True) 

	# Go to EQMS website. 
	page = await browser.new_page()
	await page.goto("https://eqms.doe.gov.my/APIMS/main")
	
	# Take a screenshot of EQMS homepage.
	await page.screenshot(path="screenshots/APIMS-screenshot.jpg") 

	# Filter Selangor. 
	await page.get_by_role("button", name="Filter").nth(1).click()
	await page.get_by_role("radio", name="Selangor").click()
	await page.get_by_role("button", name="GENERATE").click() 

	# Take a screenshot of Selangor API. 
	now = datetime.datetime.now()
	await page.screenshot(path=f"screenshots/Selangor-API-{now.strftime('%Y%m%d_%H%M%S')}.png")

	# Get API table info. 
	table = page.locator('table').nth(0)
	header = await table.locator('th').all_text_contents()
	rows = await table.locator('tbody tr').all() 
	allInfo = []
	for row in rows: 
		rowData = await row.locator('td').all_text_contents()
		rowInfo = []
		for i in rowData: 
			match = re.search(r"[a-zA-z0-9\w\s]+", i)
			text = match.group(0)
			rowInfo.append(text) 
		allInfo.append(rowInfo)
	df = pd.DataFrame(allInfo, columns=header)
	df.to_csv(path_or_buf=f"file/Selangor-API-{now.strftime('%Y%m%d_%H%M%S')}.csv", index=False)

	# Close browser. 
	await browser.close()

async def main():
	async with async_playwright() as playwright: 
		await run(playwright)

asyncio.run(main())