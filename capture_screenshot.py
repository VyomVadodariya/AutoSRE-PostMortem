import time
from playwright.sync_api import sync_playwright

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Navigating to Streamlit Dashboard...")
        page.goto("http://localhost:8501")
        page.wait_for_selector(".stApp")
        time.sleep(3)
        page.screenshot(path="assets/dashboard_overview.png", full_page=True)
        print("Saved to assets/dashboard_overview.png")
        
        # Click on Benchmarks & Results
        page.click("text=Benchmarks & Results")
        time.sleep(3)
        page.screenshot(path="assets/dashboard_benchmarks.png", full_page=True)
        print("Saved to assets/dashboard_benchmarks.png")
        
        browser.close()

if __name__ == "__main__":
    capture()
