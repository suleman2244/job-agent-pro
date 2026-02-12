import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from utils import check_language_requirements, extract_emails, clean_text, is_likely_target_language
from config import HEADLESS, REQUEST_TIMEOUT, STEPSTONE_URL

async def scrape_stepstone(search_term="Frontend", location="Germany", target_lang="English"):
    """
    Scrapes Stepstone.de for jobs posted in the past 24 hours.
    Filter for date: 'age=1'.
    """
    import os
    if os.environ.get("VERCEL"):
        print("Scraping Stepstone is not supported in Vercel environment.")
        return []

    results = []
    base_url = STEPSTONE_URL.format(keyword=search_term, location=location)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT)
            await page.wait_for_selector(".res-1v8vsm5", timeout=10000) # Card selector
        except Exception:
            await browser.close()
            return []

        job_cards = await page.query_selector_all(".res-1v8vsm5")
        
        for card in job_cards[:8]:
            title_el = await card.query_selector("h2")
            company_el = await card.query_selector(".res-v7zn8r")
            link_el = await card.query_selector("a")
            
            title = await title_el.inner_text() if title_el else ""
            company = await company_el.inner_text() if company_el else ""
            link = await link_el.get_attribute("href") if link_el else ""

            # EARLY EXIT
            if not is_likely_target_language(title, target_lang):
                continue

            if link:
                if not link.startswith("http"):
                    link = "https://www.stepstone.de" + link
                
                detail_page = await context.new_page()
                await detail_page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
                try:
                    await stealth.apply_stealth_async(detail_page)
                    await detail_page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    
                    description_el = await detail_page.query_selector(".js-app-ld-ContentBlock") or \
                                     await detail_page.query_selector(".listing-content") or \
                                     await detail_page.query_selector("body")
                    description = await description_el.inner_text() if description_el else ""
                    
                    if check_language_requirements(description, target_lang):
                        results.append({
                            "title": clean_text(title),
                            "company": clean_text(company),
                            "link": link,
                            "emails": extract_emails(description),
                            "location": location,
                            "source": "Stepstone"
                        })
                except Exception:
                    pass
                finally:
                    await detail_page.close()
        
        await browser.close()
    return results

if __name__ == "__main__":
    jobs = asyncio.run(scrape_stepstone())
    for job in jobs:
        print(f"--- \nTitle: {job['title']}\nCompany: {job['company']}\nEmails: {job['emails']}\nLink: {job['link']}\n")
