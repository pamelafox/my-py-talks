from playwright.sync_api import sync_playwright

with sync_playwright() as p:
  browser = p.chromium.launch()
  page = browser.new_page()
  page.goto("https://flaskcon.com/2025/")
  print(page.title())
  browser.close()