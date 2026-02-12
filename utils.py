import re
from langdetect import detect, DetectorFactory

# Ensure consistent language detection
DetectorFactory.seed = 0

def is_english(text):
    """Checks if the given text is English."""
    if not text or len(text.strip()) < 10:
        return False
    try:
        return detect(text) == 'en'
    except:
        return False

def extract_emails(text):
    """Extracts email addresses from text using a robust regex."""
    if not text:
        return []
    # Improved regex to catch more variations
    email_pattern = r'[a-zA-Z0-9._%+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, text)))
    
    # Prioritize 'Job' or 'HR' related emails
    hr_keywords = ['hr', 'jobs', 'careers', 'recruitment', 'bewerbung', 'career', 'personal', 'hiring']
    hr_emails = [e for e in emails if any(k in e.lower() for k in hr_keywords)]
    
    # Return formatted string: HR emails first, then others
    other_emails = [e for e in emails if e not in hr_emails]
    final_list = hr_emails + other_emails
    return final_list

def clean_text(text):
    """Cleans up whitespace, newlines, and special characters."""
    if not text:
        return ""
    # Remove excessive whitespace
    text = " ".join(text.split())
    # Basic cleaning of non-ASCII characters if needed, but keeping it simple for now
    return text.strip()

def detect_language(text):
    """Detects the language of the given text."""
    if not text or len(text.strip()) < 10:
        return 'unknown'
    try:
        return detect(text)
    except:
        return 'unknown'

def check_language_requirements(description, target_lang="English"):
    """
    Checks if the job description meets the target language requirements STENCHLY.
    If English is selected: Must be English, must NOT require German.
    If German is selected: Must be German or specifically require German.
    If French/Spanish/etc is selected: Must match that language code.
    """
    if not description:
        return False
    
    desc_lower = description.lower()
    detected = detect_language(description)
    
    # Map target strings to langdetect codes
    lang_map = {
        "English": "en",
        "German": "de",
        "French": "fr",
        "Spanish": "es",
        "Italian": "it",
        "Dutch": "nl"
    }
    
    target_code = lang_map.get(target_lang)
    
    # --- 1. ENGLISH SELECTION ---
    if target_lang == "English":
        # Must NOT have German as a hard requirement
        german_req_indicators = [
            "deutsch als muttersprache", "deutschkenntnisse", "fluent german", 
            "level b2", "level c1", "voraussetzung: deutsch", "fließend deutsch",
            "deutsch: verhandlungssicher"
        ]
        requires_german = any(i in desc_lower for i in german_req_indicators)
        if requires_german:
            return False
            
        # Is it detected as English?
        if detected == 'en':
            return True
            
        # Fallback for tech descriptions that langdetect might miss
        tech_keywords = ["react", "frontend", "flutter", "angular", "javascript", "typescript", "node", "experience", "requirements", "engineer", "developer"]
        has_strong_english = any(k in desc_lower for k in tech_keywords)
        
        # If it's something else (like German) but has no German keywords and has tech keywords, maybe.
        # But for 'Strict', if it's detected as 'de', we should probably skip.
        if detected == 'de' and "deutsch" in desc_lower:
            return False
            
        return has_strong_english

    # --- 2. GERMAN SELECTION ---
    if target_lang == "German":
        # Must be detected as de OR mention German requirements
        if detected == 'de':
            return True
        german_indicators = ["deutschkenntnisse", "deutsch", "voraussetzungen", "aufgaben", "kenntnisse"]
        return any(g in desc_lower for g in german_indicators)

    # --- 3. OTHER SPECIFIC LANGUAGES ---
    if target_code:
        # Strict match for detecting that specific language
        return detected == target_code

    # --- 4. ALL / BOTH ---
    return True

def is_likely_target_language(snippet, target_lang):
    """
    Failsafe early check on snippets to avoid opening slow detail pages.
    """
    if not snippet or target_lang in ["All", "Both"]:
        return True
    
    snippet_lower = snippet.lower()
    detected = detect_language(snippet)
    
    lang_map = {"English": "en", "German": "de", "French": "fr", "Spanish": "es", "Italian": "it"}
    target_code = lang_map.get(target_lang)
    
    if target_lang == "English":
        # If snippet is clearly German, skip
        if detected == 'de' and ("deutsch" in snippet_lower or "german" in snippet_lower):
            return False
        return True # Be lenient on snippets to avoid false negatives

    if target_lang == "German":
        # If snippet is clearly something else, skip
        if detected != 'de' and "deutsch" not in snippet_lower:
            return False
        return True

    if target_code:
        return detected == target_code or detected == 'unknown'
        
    return True

def find_hr_email(description):
    """Extracts email addresses from text using regex."""
    if not description:
        return []
    return extract_emails(description)
