from playwright.sync_api import sync_playwright
from axe_playwright_python.sync_playwright import Axe

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://pretalx.northbaypython.org/")
    results = Axe().run(page)
    print(results.response)
    browser.close()