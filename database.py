import sqlite3
import os
from datetime import datetime

DB_PATH = "jobs_agent.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Jobs Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT,
        location TEXT,
        link TEXT UNIQUE,
        emails TEXT,
        source TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'new'
    )
    ''')
    
    # Scans Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        roles TEXT,
        location TEXT,
        language TEXT,
        job_count INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_jobs(jobs_list):
    """Saves a list of job dictionaries to the database."""
    if not jobs_list:
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    new_jobs_count = 0
    for job in jobs_list:
        try:
            # Convert emails list to string
            emails_str = "\n".join(job.get('emails', [])) if isinstance(job.get('emails'), list) else job.get('emails', '')
            
            cursor.execute('''
            INSERT OR IGNORE INTO jobs (title, company, location, link, emails, source)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                job.get('title'),
                job.get('company'),
                job.get('location'),
                job.get('link'),
                emails_str,
                job.get('source')
            ))
            if cursor.rowcount > 0:
                new_jobs_count += 1
        except Exception as e:
            print(f"Error saving job {job.get('title')}: {e}")
            
    conn.commit()
    conn.close()
    return new_jobs_count

def log_scan(roles, location, language, count):
    """Logs a search session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO scans (roles, location, language, job_count)
    VALUES (?, ?, ?, ?)
    ''', (", ".join(roles), location, language, count))
    conn.commit()
    conn.close()

def get_all_jobs(limit=100):
    """Returns all jobs from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats():
    """Returns basic stats about the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM jobs')
    total_jobs = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) as total FROM scans')
    total_scans = cursor.fetchone()['total']
    conn.close()
    return {"total_jobs": total_jobs, "total_scans": total_scans}
