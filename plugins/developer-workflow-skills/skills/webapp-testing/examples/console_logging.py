import tempfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

# Example: capture console messages and uncaught page errors while exercising a flow.

URL = "http://localhost:5173"  # Replace with your URL

out_dir = Path(tempfile.mkdtemp(prefix="webapp-testing-"))
console_lines: list[str] = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.on("console", lambda msg: console_lines.append(f"[{msg.type}] {msg.text}"))
    page.on("pageerror", lambda err: console_lines.append(f"[pageerror] {err}"))

    page.goto(URL)
    page.get_by_role("link", name="Dashboard").click()
    # Web-first assertion: retries until the dashboard renders, so no sleep is needed.
    expect(page.get_by_role("heading", name="Dashboard")).to_be_visible()

    browser.close()

log_path = out_dir / "console.log"
log_path.write_text("\n".join(console_lines))
print(f"Captured {len(console_lines)} console messages")
print(f"Logs saved to: {log_path}")
