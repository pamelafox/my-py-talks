from playwright.sync_api import Page

def test_violations(page: Page, axe_pytest_snapshot):
    page.goto("https://2023.northbaypython.org/")
    axe_pytest_snapshot(page)