from fastapi import FastAPI, BackgroundTasks, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from main import run_job_agent, scraping_status
from config import OUTPUT_FILENAME
from database import init_db, get_all_jobs, get_stats

app = FastAPI()

# SaaS Setup: Initialize Database
init_db()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from pydantic import BaseModel
from typing import List, Optional

class SearchFilters(BaseModel):
    roles: List[str]
    location: str
    language: str # 'English', 'German', or 'Both'

# Shared state
scraping_state = {
    "active": False,
    "progress": 0,
    "message": "Idle",
    "job_count": 0,
    "ready_to_download": False,
    "current_role": "",
    "filters": None
}

@app.get("/api/status")
async def get_status():
    return scraping_state

async def status_updater(new_state):
    global scraping_state
    scraping_state.update(new_state)

async def search_task(roles: List[str], location: str, language: str):
    global scraping_state
    report_path = await run_job_agent(
        roles=roles, 
        location=location, 
        language=language,
        status_callback=status_updater
    )
    if report_path:
        scraping_state["ready_to_download"] = True
    else:
        scraping_state["ready_to_download"] = False
    scraping_state["active"] = False

@app.post("/api/start-search")
async def start_search(filters: SearchFilters, background_tasks: BackgroundTasks):
    global scraping_state
    if scraping_state["active"]:
        return {"error": "Search already in progress"}
    
    if os.environ.get("VERCEL"):
        scraping_state = {
            "active": False,
            "progress": 0,
            "message": "Scraping not supported on Vercel Serverless. Run locally for full functionality.",
            "job_count": 0,
            "ready_to_download": False,
            "current_role": "",
            "filters": filters.dict()
        }
        return {"message": "Scraping not supported on Vercel", "unsupported": True}

    scraping_state = {
        "active": True,
        "progress": 0,
        "message": "Starting...",
        "job_count": 0,
        "ready_to_download": False,
        "current_role": "",
        "filters": filters.dict()
    }
    background_tasks.add_task(search_task, filters.roles, filters.location, filters.language)
    return {"message": "Search started"}

@app.get("/api/download-report")
async def download_report():
    print(f"DEBUG: Export download requested. File exists: {os.path.exists(OUTPUT_FILENAME)}")
    if os.path.exists(OUTPUT_FILENAME):
        with open(OUTPUT_FILENAME, "rb") as f:
            file_content = f.read()
        
        # Manually construct the response to avoid any auto-header conflicts
        return Response(
            content=file_content,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                "Content-Disposition": 'attachment; filename="jobs_report.xlsx"',
                "Content-Length": str(len(file_content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
            }
        )
    return {"error": "File not found"}

# --- SAAS ENDPOINTS ---

@app.get("/api/stats")
async def get_db_stats():
    """Returns total jobs and scans from DB."""
    return get_stats()

@app.get("/api/jobs")
async def get_saved_jobs(limit: int = 50):
    """Returns recent job leads from DB."""
    return get_all_jobs(limit=limit)

# Serve React production build
react_build_path = os.path.join(os.getcwd(), "web-app", "dist")

if os.path.exists(react_build_path):
    # Serve index.html for the root
    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(react_build_path, "index.html"))

    # Mount the rest of the assets
    app.mount("/", StaticFiles(directory=react_build_path), name="static")
else:
    print(f"Warning: React build at {react_build_path} not found.")
    # Fallback to legacy static if it exists
    if os.path.exists("static"):
        app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Kill any existing server on 8000
    os.system("pkill -f 'uvicorn server:app' || true")
    uvicorn.run(app, host="0.0.0.0", port=8000)
