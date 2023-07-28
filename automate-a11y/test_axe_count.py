from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page

def test_a11y(page: Page):
    page.goto("https://www.pamelafox.org")
    results = Axe().run(page)
    assert results.violations_count == 0, results.generate_report()