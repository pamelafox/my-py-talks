from playwright.sync_api import Page, expect

def test_buy_tickets(page: Page) -> None:
    page.goto("https://pybay.org/")
    assert page.title() == "PyBay 2025 - 10th Annual Bay Area Python Dev Conference - Welcome to PyBay!"
    expect(page.get_by_role("heading", level=2)).to_contain_text("What's New At PyBay This Year?")
    page.get_by_role("link", name="Learn More").click()
    with page.expect_popup() as popup_event:
        page.get_by_role("link", name="Buy Tickets!").click()
    tickets_page = popup_event.value
    assert tickets_page.url == "https://pretix.eu/bapya/pybay-2025/"