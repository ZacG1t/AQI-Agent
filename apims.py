import datetime
import re
import numpy as np 
import pandas as pd 
from pathlib import Path

import sqlite3 
from sqlalchemy import create_engine

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
			print(f"Actual: {len(headers)} {headers}") 
			print(f"Expected: {len(expected_headers)} {expected_headers}")
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
	# await page.screenshot(path=ss_path)
	
	table = page.locator("table").first 
	headers = await table.locator("th").all_text_contents()
	if headers[-1] == '': 
		del headers[-1]

	rows = [] 
	for row in await table.locator("tbody tr").all(): 
		row_data = [cell.strip() for cell in await row.locator("td").all_text_contents()]
		row_data[headers.index("LOCATION")] = row_data[headers.index("LOCATION")].title() 
		rows.append(row_data)

	return headers, rows


def save_csv(headers, rows, path): 
	df = pd.DataFrame(rows, columns=headers) 
	df = df.drop(df.columns[[0, 3]], axis='columns')  
	df.to_csv(path_or_buf=path, index=False) 
	print(f"File saved to {path}") 

	engine = create_engine("sqlite:///database/api.db") 
	with engine.begin() as connection:
		df.to_sql(name="api", con=engine, if_exists="append") 
		print(f"API saved to db.") 

"""
def add_to_db(): 
	con = sqlite3.connect("api.db") 
	cur = con.cursor() 
	cur.execute("CREATE TABLE api(State Location 9:00 10:00 11:00 12:00 13:00 14:00 15:00 16:00 17:00 18:00 19:00 20:00 21:00 22:00 23:00 0:00 1:00 2:00 3:00 4:00 5:00 6:00 7:00 8:00 9:00") 

	res = cur.execute("SELECT api FROM sqlite_master") 
	res.fetchone()
"""

async def main():
	async with async_playwright() as playwright: 
		await run(playwright)

if __name__ == "__main__": 
	asyncio.run(main())