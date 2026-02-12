import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from utils import check_language_requirements, extract_emails, clean_text, is_likely_target_language
from config import HEADLESS, REQUEST_TIMEOUT, INDEED_URL

async def scrape_indeed(search_term="Frontend", location="Germany", target_lang="English"):
    """
    Scrapes Indeed.de for jobs posted in the past 24 hours.
    Filter for date: 'fromage=1'.
    """
    results = []
    base_url = INDEED_URL.format(keyword=search_term, location=location)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"Navigating to Indeed: {base_url}")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT)
            await page.wait_for_selector(".job_seen_beacon", timeout=10000)
        except Exception:
            print(f"Error navigating to Indeed: {e}") # Keep this print for debugging
            await browser.close()
            return []

        job_cards = await page.query_selector_all(".job_seen_beacon")
        print(f"Found {len(job_cards)} potential job listings on Indeed for {search_term}.")

        for card in job_cards[:8]:
            title_el = await card.query_selector("h2.jobTitle")
            company_el = await card.query_selector("[data-testid='company-name']")
            link_el = await card.query_selector("h2.jobTitle a")
            snippet_el = await card.query_selector(".job-snippet") # Indeed has snippets!
            
            title = await title_el.inner_text() if title_el else ""
            company = await company_el.inner_text() if company_el else ""
            link = await link_el.get_attribute("href") if link_el else ""
            snippet = await snippet_el.inner_text() if snippet_el else ""

            # EARLY EXIT with Snippet check (Very effective on Indeed)
            if not is_likely_target_language(title + " " + snippet, target_lang):
                continue

            if link:
                if not link.startswith("http"):
                    link = "https://de.indeed.com" + link
                
                detail_page = await context.new_page()
                await detail_page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
                try:
                    await stealth.apply_stealth_async(detail_page)
                    await detail_page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    
                    description_el = await detail_page.query_selector("#jobDescriptionText") or \
                                     await detail_page.query_selector("body")
                    description = await description_el.inner_text() if description_el else ""
                    
                    if check_language_requirements(description, target_lang):
                        results.append({
                            "title": clean_text(title),
                            "company": clean_text(company),
                            "link": link,
                            "emails": extract_emails(description),
                            "location": location,
                            "source": "Indeed"
                        })
                except Exception:
                    print(f"Error scraping Indeed detail {link}: {e}") # Keep this print for debugging
                    pass
                finally:
                    await detail_page.close()
        
        await browser.close()
    return results

if __name__ == "__main__":
    jobs = asyncio.run(scrape_indeed())
    for job in jobs:
        print(f"--- \nTitle: {job['title']}\nCompany: {job['company']}\nEmails: {job['emails']}\nLink: {job['link']}\n")
