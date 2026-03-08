from collections import Counter
from src.clients.adzuna_client import fetch_jobs, extract_job_descriptions
from src.clients.llm_client import extract_skills_from_text

def analyze_job_skills(role: str, experience_level: str) -> list[tuple[str, int]]:
    """
    Orchestrates the job fetching, skill extraction, and aggregation pipeline.
    """
    # 1. Fetch 30-50 jobs (Using 50 as default max in our adzuna fetcher)
    # Appending experience level hint to the search query often causes Adzuna to return 0 results.
    # Therefore, we just search the role and filter implicitly if we want, but for now
    # fetching just the role guarantees we have text to analyze.
    search_query = role
    jobs = fetch_jobs(role=search_query, location="in", results_per_page=50)
    
    if not jobs:
        return []

    # 2. Extract job descriptions and combine text
    combined_text = extract_job_descriptions(jobs)
    
    if not combined_text.strip():
        return []

    # 3. Call LLM for extraction
    skills = extract_skills_from_text(combined_text)

    # 4. Normalization + Frequency Aggregation
    # Since the LLM extracted skills for the whole batch of text at once,
    # the LLM output is a deduped list of skills present in the text block.
    # To get proper frequencies across multiple jobs, we should ideally chunk text 
    # per job or smaller batches. 
    # Because of constraints and simplicity from requirements:
    # "Send combined descriptions to LLM" -> The LLM will just return the skills it found.
    # If the LLM returns multiple instances, we count them. Let's do a simple count.
    # Wait: If LLM just lists skills, frequency per job is lost.
    # We will refine this by counting occurrences of each extracted skill in the combined text.
    
    skill_counts = Counter()
    combined_lower = combined_text.lower()
    
    for skill in skills:
        # A simple string match count in the raw text to establish frequency
        # This is a robust deterministic way to rank them after extraction.
        # We add spaces around or just search. Small words might false trigger if we don't word-boundary, 
        # but for simplicity we'll do simple substring or word boundary.
        import re
        pattern = r'\b' + re.escape(skill) + r'\b'
        count = len(re.findall(pattern, combined_lower))
        if count > 0:
            skill_counts[skill] = count
            
    # Rank top 15 skills
    top_skills = skill_counts.most_common(15)
    return top_skills
