import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            print("Playwright: Chromium launched successfully.")
            await browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")

if __name__ == "__main__":
    asyncio.run(test_playwright())
