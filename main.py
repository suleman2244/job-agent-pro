import asyncio
from scraper_linkedin import scrape_linkedin
from scraper_stepstone import scrape_stepstone
from scraper_indeed import scrape_indeed
from scraper_startup import scrape_startup_jobs
from exporter import export_to_excel
from database import save_jobs, log_scan
from config import ROLES, LOCATION

# Global status for the SaaS API
scraping_status = {"active": False, "progress": 0, "message": "Idle", "job_count": 0}

async def run_job_agent(roles=ROLES, location=LOCATION, language="Both", status_callback=None):
    global scraping_status
    scraping_status = {
        "active": True, 
        "progress": 0, 
        "message": "Initializing...", 
        "job_count": 0,
        "current_role": ""
    }
    if status_callback: await status_callback(scraping_status)

    all_jobs = []
    total_steps = len(roles)
    
    for i, role in enumerate(roles):
        scraping_status["message"] = f"Deploying agent for {role}..."
        scraping_status["current_role"] = role
        scraping_status["progress"] = int((i / total_steps) * 100)
        if status_callback: await status_callback(scraping_status)
        
        # Run scrapers for each role
        scraping_status["message"] = f"Gathering {role} leads (LinkedIn, Stepstone, Indeed, Startup)..."
        if status_callback: await status_callback(scraping_status)
        
        results = await asyncio.gather(
            scrape_linkedin(role, location, language),
            scrape_stepstone(role, location, language),
            scrape_indeed(role, location, language),
            scrape_startup_jobs(role, location, language)
        )
        
        # Flatten and filter
        seen_links = {job['link'] for job in all_jobs}
        new_count = 0
        for portal_results in results:
            for job in portal_results:
                if job['link'] not in seen_links:
                    all_jobs.append(job)
                    seen_links.add(job['link'])
                    new_count += 1
        
        scraping_status["job_count"] = len(all_jobs)
        scraping_status["message"] = f"Role {role} complete: Scanned {new_count} new strict matches."
        if status_callback: await status_callback(scraping_status)
    
    scraping_status["progress"] = 100
    scraping_status["message"] = "Exporting results..."
    if status_callback: await status_callback(scraping_status)

    if all_jobs:
        # SaaS Upgrade: Save to Database
        new_count = save_jobs(all_jobs)
        log_scan(roles, location, language, len(all_jobs))
        
        report_path = export_to_excel(all_jobs)
        scraping_status["message"] = f"Finished! Found {len(all_jobs)} total ({new_count} new saved)."
        scraping_status["active"] = False
        if status_callback: await status_callback(scraping_status)
        return report_path
    else:
        scraping_status["message"] = "No jobs found."
        scraping_status["active"] = False
        if status_callback: await status_callback(scraping_status)
        return None

if __name__ == "__main__":
    asyncio.run(run_job_agent())
