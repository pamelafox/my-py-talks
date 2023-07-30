from playwright.sync_api import Page, expect

def test_click_tickets(page: Page):
    page.goto("https://2023.northbaypython.org/")
    page.get_by_role("link", name="Tickets on sale now!").click()
    expect(page.locator("main")).to_contain_text("tickets are available")