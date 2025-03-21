from playwright.sync_api import sync_playwright

JENKINS_URL = "http://192.168.206.182:8081/"
USERNAME = "admin"
PASSWORD = "admin"

with sync_playwright() as p:
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()

    try:
        # Configure default timeouts
        page.set_default_timeout(60000)  # Global timeout 60s

        # Login with explicit navigation wait
        page.goto(JENKINS_URL, wait_until="networkidle")
        page.fill('#j_username', USERNAME)
        page.fill('#j_password', PASSWORD)
        page.click('button[name="Submit"]', timeout=15000)

        # Manage Jenkins section with combined wait/click
        page.wait_for_selector('a[href="/manage"]', state="attached")
        with page.expect_navigation():
            page.click('a[href="/manage"]')

        # Security Realm with enhanced selector and explicit waits
        security_realm_selector = 'a[href*="securityRealm"]'  # More flexible selector
        page.wait_for_selector(security_realm_selector, state="visible")

        # Click with multiple assurances
        page.click(
            security_realm_selector,
            timeout=45000,  # Extended per-action timeout
            no_wait_after=False
        )

        # User listing with DOM stability check
        page.wait_for_load_state("domcontentloaded")
        users = page.locator('table#people tr td a').all_text_contents()

        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- {user}")

    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        browser.close()
