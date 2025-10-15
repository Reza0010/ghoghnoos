from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://localhost:3000")

    # Use expect to wait for the button to be visible before clicking
    settings_button = page.get_by_role("button", name="Settings")
    expect(settings_button).to_be_visible(timeout=30000)
    settings_button.click()

    # Wait for the input to be visible
    api_key_input = page.get_by_placeholder("Enter new API key")
    expect(api_key_input).to_be_visible()
    api_key_input.click()
    api_key_input.fill("test-api-key")

    # Wait for the add button to be visible
    add_key_button = page.get_by_role("button", name="Add Key")
    expect(add_key_button).to_be_visible()
    add_key_button.click()

    # Wait for the new key to appear in the list
    new_key_element = page.locator("text=test-api-key")
    expect(new_key_element).to_be_visible()

    page.screenshot(path="jules-scratch/verification/verification.png")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
