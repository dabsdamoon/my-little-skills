import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

# Example: driving a local HTML file through a file:// URL.

html_file = Path("path/to/your/file.html").resolve()
out_dir = Path(tempfile.mkdtemp(prefix="webapp-testing-"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(html_file.as_uri())
    page.screenshot(path=out_dir / "static_page.png", full_page=True)

    page.get_by_role("button", name="Click Me").click()
    # get_by_label needs a <label> or aria-label. A field without one is an
    # accessibility finding; record it, then fall back to page.locator("#name").
    page.get_by_label("Name").fill("John Doe")
    page.get_by_label("Email").fill("john@example.com")
    page.get_by_role("button", name="Submit").click()

    # Assert the outcome the spec describes instead of sleeping.
    expect(page.get_by_text("Thanks for signing up")).to_be_visible()

    page.screenshot(path=out_dir / "after_submit.png", full_page=True)
    browser.close()

print(f"Screenshots saved to {out_dir}")
