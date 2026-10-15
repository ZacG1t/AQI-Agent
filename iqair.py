from playwright.sync_api import sync_playwright, Playwright

def run(playwright: Playwright):
	# Launch a browser. 
	chromium = playwright.chromium
	browser = chromium.launch(headless=False) 

	# Go to www.iqair.com
	page = browser.new_page()
	page.goto("https://www.iqair.com")
	
	# Take a screenshot of iqair.com homepage.
	page.screenshot(path="screenshots/iqair-screenshot.jpg") 

	# Fill location and search. 
	#page.get_by_role("search").fill("Petaling Jaya")
	page.get_by_role("search").highlight()

	# Close browser. 
	browser.close()

with sync_playwright() as playwright: 
	run(playwright)