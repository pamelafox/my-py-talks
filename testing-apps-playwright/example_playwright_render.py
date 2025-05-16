from playwright.sync_api import sync_playwright

with sync_playwright() as p:
  browser = p.chromium.launch()
  page = browser.new_page()
  page.goto("https://2023.northbaypython.org/")
  print(page.title())
  browser.close()