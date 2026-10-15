import datetime
import re
import numpy as np 
import pandas as pd 
from pathlib import Path

import asyncio
from playwright.async_api import async_playwright, Playwright

async def run(playwright: Playwright):
	# Create directories. 
	Path("screenshots").mkdir(exist_ok=True) 
	Path("file").mkdir(exist_ok=True)

	# Launch a browser. 
	chromium = playwright.chromium
	browser = await chromium.launch(headless=True) 

	# Go to EQMS website. 
	page = await browser.new_page()
	await page.goto("https://eqms.doe.gov.my/APIMS/main")
	
	# Take a screenshot of APIMS homepage.
	await page.screenshot(path="screenshots/APIMS-screenshot.jpg") 

	# Filter state. 
	states = ["Selangor", "Negeri Sembilan", "Pulau Pinang"]
	all_info = []
	expected_headers = None
	for state in states:
		headers, rows = await scrape_state(page, state) 

		if expected_headers is None: 
			expected_headers = headers 
		elif headers != expected_headers: 
			raise ValueError(f"Table columns changed for {state}")

		all_info.extend(rows) 

	# Save csv. 
	now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") 
	csv_path = f"file/Malaysia-API-{now}.csv" 

	save_csv(expected_headers, all_info, csv_path)

	# Close browser. 
	await browser.close()


async def scrape_state(page, state): 
	filter_button = page.get_by_role("button", name="Filter").nth(1) 
	await filter_button.click() 
	await page.get_by_role("radio", name=state).click() 
	await page.get_by_role("button", name="GENERATE").click() 

	# Take a screenshot of state API. 
	now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
	ss_path = f"screenshots/{state}-API-{now}.png"
	await page.screenshot(path=ss_path)
	
	table = page.locator("table").first 
	headers = await table.locator("th").all_text_contents()

	rows = [] 
	for row in await table.locator("tbody tr").all(): 
		row_data = [cell.strip() for cell in await row.locator("td").all_text_contents()]
		row_data[headers.index("LOCATION")] = row_data[headers.index("LOCATION")].title()
		cells = await row.locator("td").all_text_contents() 
		for cell in cells: 
			match = re.search(r"[a-zA-Z0-9\w\s]+", cell) 
			cell = match.group(0)
		rows.append([cell.strip() for cell in cells]) 

	return headers, rows


def save_csv(headers, rows, path): 
	df = pd.DataFrame(rows, columns=headers) 
	df = df.drop(columns="NO.") 
	df.to_csv(path_or_buf=path, index=False) 
	print(f"File saved to {path}")


async def main():
	async with async_playwright() as playwright: 
		await run(playwright)

if __name__ == "__main__": 
	asyncio.run(main())