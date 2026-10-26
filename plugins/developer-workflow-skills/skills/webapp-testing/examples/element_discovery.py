import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

# Example: reconnaissance. Print the accessibility tree and list interactive elements,
# then write locators (get_by_role / get_by_label / get_by_text) from what you see.

URL = "http://localhost:5173"  # Replace with your URL

out_dir = Path(tempfile.mkdtemp(prefix="webapp-testing-"))

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)
    # Readiness: wait for an element that only renders once the app has loaded.
    expect(page.get_by_role("heading").first).to_be_visible()

    # Roles and accessible names: the vocabulary get_by_role() matches against.
    print(page.aria_snapshot())

    buttons = page.get_by_role("button").all()
    print(f"\nFound {len(buttons)} buttons:")
    for i, button in enumerate(buttons):
        label = button.inner_text().strip() if button.is_visible() else "[hidden]"
        print(f"  [{i}] {label}")

    links = page.get_by_role("link").all()
    print(f"\nFound {len(links)} links:")
    for link in links[:5]:
        print(f"  - {link.inner_text().strip()} -> {link.get_attribute('href')}")

    inputs = page.locator("input, textarea, select").all()
    print(f"\nFound {len(inputs)} input fields:")
    for field in inputs:
        name = field.get_attribute("name") or field.get_attribute("id") or "[unnamed]"
        print(f"  - {name} ({field.get_attribute('type') or 'text'})")

    screenshot = out_dir / "page_discovery.png"
    page.screenshot(path=screenshot, full_page=True)
    print(f"\nScreenshot saved to {screenshot}")

    browser.close()
