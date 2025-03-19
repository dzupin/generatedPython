from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Launch Firefox
    browser = p.firefox.launch(headless=False)  # Set headless=False to see the browser
    page = browser.new_page()

    # Navigate to a website
    page.goto("https://www.google.com")

    # Take a screenshot
    page.screenshot(path="example.png")

    # Close browser
    browser.close()

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    page.goto("https://wikipedia.org")
    # Take a screenshot
    page.screenshot(path="example01.png")

    # Type into search box
    page.fill("#searchInput", "Artificial Intelligence")
    # Take a screenshot
    page.screenshot(path="example02.png")

    # Click search button
    page.click("button:has-text('Search')")
    # Take a screenshot
    page.screenshot(path="example03.png")

    # Wait for results
    page.wait_for_selector("#firstHeading")
    # Take a screenshot
    page.screenshot(path="example04.png")
    print(page.title())
    browser.close()
