import os

# Job search parameters
ROLES = ["Frontend Developer", "React Native Developer", "Flutter Developer", "Angular Developer"]
LOCATION = "Germany"
POSTED_LAST_24H = True

# Scraping settings
HEADLESS = True  # Set to False to see the browser in action
REQUEST_TIMEOUT = 60000  # 60 seconds

# Export settings
if os.environ.get("VERCEL"):
    OUTPUT_FILENAME = "/tmp/jobs_report.xlsx"
else:
    OUTPUT_FILENAME = "jobs_report.xlsx"

# Search URLs (Templates)
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/?f_TPR=r86400&keywords={keyword}&location={location}"
STEPSTONE_URL = "https://www.stepstone.de/jobs/{keyword}/in-{location}?radius=0&age=1"
INDEED_URL = "https://de.indeed.com/jobs?q={keyword}&l={location}&fromage=1"
STARTUP_JOBS_URL = "https://www.startupjobs.com/jobs?q={keyword}&l={location}"
