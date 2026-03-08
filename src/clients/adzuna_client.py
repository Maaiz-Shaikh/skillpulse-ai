import requests
import json
from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY

class AdzunaClientError(Exception):
    pass

def fetch_jobs(role: str, location: str = "in", results_per_page: int = 50) -> list[dict]:
    """
    Fetches job listings from Adzuna's API.
    By default, location is 'in' (India).
    """
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError("Adzuna API credentials are not set in the environment.")
    
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
    
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": role,
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise AdzunaClientError(f"Error fetching from Adzuna API: {response.status_code} - {response.text}")
        
    data = response.json()
    return data.get("results", [])

def extract_job_descriptions(jobs: list[dict]) -> str:
    """
    Combines all job descriptions into a single text block.
    """
    descriptions = [job.get("description", "") for job in jobs if job.get("description")]
    return "\n\n".join(descriptions)
