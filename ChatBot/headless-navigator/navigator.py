from pathlib import Path
from playwright.sync_api import sync_playwright

# Create screenshot folder
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def screenshot(page, step):
    path = SCREENSHOT_DIR / f"{step}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"Screenshot saved: {path.resolve()}")


with sync_playwright() as p:
    # Step 1: Launch browser
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    screenshot(page, "01_browser_started")

    # Step 2: Open website
    page.goto(
        "https://www.selenium.dev/selenium/web/web-form.html",
        wait_until="domcontentloaded"
    )
    page.locator("input[name='my-text']").wait_for()
    screenshot(page, "02_website_opened")

    # Step 3: Enter text
    page.locator("input[name='my-text']").fill(
        "Hello from Playwright"
    )
    screenshot(page, "03_text_entered")

    # Step 4: Select dropdown option
    page.locator("select[name='my-select']").select_option("2")
    screenshot(page, "04_dropdown_selected")

    # Step 5: Submit form
    page.get_by_role("button", name="Submit").click()
    page.locator("#message").wait_for()
    screenshot(page, "05_form_submitted")

    # Step 6: Capture final result
    print("Final URL:", page.url)
    print("Result:", page.locator("#message").inner_text())
    screenshot(page, "06_final_result")

    browser.close()
    print("Automation completed!")
