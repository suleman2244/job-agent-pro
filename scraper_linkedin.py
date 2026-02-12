import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from utils import check_language_requirements, extract_emails, clean_text, is_likely_target_language
from config import HEADLESS, REQUEST_TIMEOUT, LINKEDIN_URL

async def scrape_linkedin(search_term="Frontend", location="Germany", target_lang="English"):
    """
    Scrapes LinkedIn with optimization.
    """
    if os.environ.get("VERCEL"):
        print("Scraping LinkedIn is not supported in Vercel environment.")
        return []

    results = []
    base_url = LINKEDIN_URL.format(keyword=search_term, location=location)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        # Optimization: Block unnecessary resources
        page = await context.new_page()
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
        
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        
        print(f"Navigating to LinkedIn: {base_url}")
        try:
            await page.goto(base_url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT)
            await page.wait_for_selector(".base-card", timeout=10000)
        except Exception as e:
            print(f"Error navigating to LinkedIn: {e}")
            if "Timeout" in str(e):
                print("Hint: LinkedIn might be slow or blocking requests. Try increasing REQUEST_TIMEOUT.")
            await browser.close()
            return []

        job_cards = await page.query_selector_all(".base-card")
        print(f"Found {len(job_cards)} potential job listings on LinkedIn for {search_term}.")

        for card in job_cards[:8]: # Slightly increased limit but with faster Filtering
            title_el = await card.query_selector(".base-search-card__title")
            company_el = await card.query_selector(".base-search-card__subtitle")
            link_el = await card.query_selector("a.base-card__full-link")
            
            title = await title_el.inner_text() if title_el else "N/A"
            company = await company_el.inner_text() if company_el else "N/A"
            link = await link_el.get_attribute("href") if link_el else "N/A"
            
            # EARLY EXIT: Check if title/snippet suggests wrong language
            if not is_likely_target_language(title, target_lang):
                continue

            if link != "N/A":
                detail_page = await context.new_page()
                # Also block resources in detail page
                await detail_page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff2}", lambda route: route.abort())
                try:
                    await stealth.apply_stealth_async(detail_page)
                    await detail_page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    
                    # Check for authwall
                    if "authwall" in detail_page.url:
                        print(f"Skipping LinkedIn detail due to authwall: {link}")
                        continue

                    description_el = await detail_page.query_selector(".description__text") or \
                                     await detail_page.query_selector(".show-more-less-html__markup") or \
                                     await detail_page.query_selector("body")
                    description = await description_el.inner_text() if description_el else ""
                    
                    if check_language_requirements(description, target_lang):
                        emails = extract_emails(description)
                        results.append({
                            "title": clean_text(title),
                            "company": clean_text(company),
                            "link": link,
                            "emails": emails,
                            "location": location,
                            "source": "LinkedIn"
                        })
                except Exception:
                    pass
                finally:
                    if not detail_page.is_closed():
                        await detail_page.close()

        await browser.close()
    return results

if __name__ == "__main__":
    jobs = asyncio.run(scrape_linkedin())
    for job in jobs:
        print(f"--- \nTitle: {job['title']}\nCompany: {job['company']}\nEmails: {job['emails']}\nLink: {job['link']}\n")
