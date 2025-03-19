import os
from playwright.sync_api import sync_playwright

'''
Info how to create virtual environment for python and install playwright and firefox support in there:  
cd /QA
mkdir myProject 
cd /QA/myProject
python3 -m venv playwright_env
source playwright_env/bin/activate
pip install playwright
playwright install firefox 
'''

# Create download directory if it doesn't exist
os.makedirs('pdf_downloads', exist_ok=True)

with sync_playwright() as pw:
    browser = pw.firefox.launch(headless=False)
    context = browser.new_context(accept_downloads=True)  # Enable downloads
    page = context.new_page()

    try:
        # Navigate to page
        page.goto("https://arxiv.org/search", wait_until="networkidle")

        # Fill search form
        page.get_by_placeholder("Search term...").fill("mainframe")

        # Click second search button
        page.get_by_role("button", name="Search").nth(1).click()

        # Wait for results
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("//a[contains(@href, '/pdf/')]")

        # Get PDF links and download them
        pdf_links = page.locator("//a[contains(@href, '/pdf/')]").all()
        print(f"Found {len(pdf_links)} PDFs to download:")

        for link in pdf_links:
            with page.expect_download() as download_info:
                link.click()
            download = download_info.value
            # Save file with original name
            file_path = os.path.join('pdf_downloads', download.suggested_filename)
            download.save_as(file_path)
            print(f"Downloaded: {file_path}")

        # Final outputs
        print("\nPage title:", page.title())
        page.screenshot(path="arxiv_search_results.png", full_page=True)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        context.close()
        browser.close()
