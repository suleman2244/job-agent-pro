import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from utils import check_language_requirements, extract_emails, clean_text, is_likely_target_language
from config import HEADLESS, REQUEST_TIMEOUT, STARTUP_JOBS_URL

async def scrape_startup_jobs(search_term="Frontend", location="Germany", target_lang="English"):
    """
    Scrapes StartupJobs.com for tech startup jobs.
    """
    results = []
    base_url = STARTUP_JOBS_URL.format(keyword=search_term, location=location)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        # Optimization: Block unnecessary resources
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
        
        print(f"Navigating to StartupJobs: {base_url}")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT)
            # Wait for job list
            await page.wait_for_selector(".job-list-item", timeout=10000)
        except Exception as e:
            print(f"Error navigating to StartupJobs: {e}")
            await browser.close()
            return []

        job_cards = await page.query_selector_all(".job-list-item")
        print(f"Found {len(job_cards)} potential job listings on StartupJobs.")

        for card in job_cards[:8]: # Limiting to 8 for demonstration/efficiency
            title_el = await card.query_selector(".job-list-item-title")
            company_el = await card.query_selector(".job-list-item-company")
            link_el = await card.query_selector("a")
            
            title = await title_el.inner_text() if title_el else ""
            company = await company_el.inner_text() if company_el else ""
            link = await link_el.get_attribute("href") if link_el else ""

            # EARLY EXIT: Snippet check
            if not is_likely_target_language(title, target_lang):
                continue

            if link:
                if not link.startswith("http"):
                    link = "https://www.startupjobs.com" + link
                
                detail_page = await context.new_page()
                await detail_page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
                try:
                    await detail_page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    
                    description_el = await detail_page.query_selector(".job-description") or await detail_page.query_selector("body")
                    description = await description_el.inner_text() if description_el else ""
                    
                    if check_language_requirements(description, target_lang):
                        emails = extract_emails(description)
                        results.append({
                            "title": clean_text(title),
                            "company": clean_text(company),
                            "link": link,
                            "emails": emails,
                            "location": location,
                            "source": "StartupJobs"
                        })
                except Exception as e:
                    print(f"Error scraping detail {link}: {e}")
                finally:
                    await detail_page.close()
        
        await browser.close()
    return results

if __name__ == "__main__":
    jobs = asyncio.run(scrape_startup_jobs())
    for job in jobs:
        print(f"--- \nTitle: {job['title']}\nCompany: {job['company']}\nEmails: {job['emails']}\nLink: {job['link']}\n")
