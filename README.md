# 🤖 Job Search Agent (Germany Edition)

A high-performance Python agent designed to find English-speaking developer roles in Germany across multiple platforms.

## ✨ Features
- **Multi-Platform Scraping**: Support for LinkedIn, Indeed, Stepstone, and GermanTechJobs (Startup focus).
- **Intelligent Filtering**: Automatically detects English language requirements and highlights if German is a plus.
- **Contact Extraction**: Scrapes job descriptions for HR contact emails.
- **Role Specific**: Targeted at Frontend, React Native, Flutter, and Angular roles.
- **Professional Export**: Generates a clean, formatted Excel spreadsheet (`jobs_report.xlsx`).
- **Easy Customization**: All settings centralized in `config.py`.

## 🚀 Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install pandas openpyxl xlsxwriter playwright playwright-stealth langdetect
   ```

2. **Setup Playwright**:
   ```bash
   playwright install chromium
   ```

3. **Run the SaaS Web App**:
   ```bash
   python server.py
   ```
   Open `http://localhost:8000` in your browser.

4. **Run CLI Version** (Optional):
   ```bash
   python main.py
   ```

## ⚙️ Configuration
Open `config.py` to modify:
- `ROLES`: List of job titles to search for.
- `LOCATION`: Targeted location (default: Germany).
- `HEADLESS`: Set to `False` to watch the browser work.

## 📊 Exported Data
The resulting Excel file includes:
- **Title**: Job designation.
- **Company**: Hiring organization.
- **Location**: Work location.
- **Link**: Direct URL to the posting.
- **Emails**: Extracted HR contact emails.
- **Source**: Platform where the job was found.

---
*Created for specialized job search automation.*
