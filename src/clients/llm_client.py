import requests
import json
from src.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL
from src.models.schemas import SkillExtraction

class LLMClientError(Exception):
    pass

def extract_skills_from_text(text: str) -> list[str]:
    """
    Sends the text to an LLM to extract technical skills.
    Defaults to generating an OpenAI-compatible payload (e.g., OpenRouter).
    """
    if not LLM_API_KEY or LLM_API_KEY == "your_llm_api_key_here":
        raise ValueError("LLM_API_KEY is not configured correctly.")
        
    base_url = "https://openrouter.ai/api/v1/chat/completions"
    model = LLM_MODEL or "meta-llama/llama-3-8b-instruct:free"

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Truncate text if it's too long to prevent context window overflow
    # ~4000 chars is usually safe for smaller free models
    if len(text) > 8000:
        text = text[:8000]

    prompt = f"""
    Analyze the following job descriptions and extract all technical skills mentioned.
    Technical skills include programming languages, frameworks, databases, cloud platforms, DevOps tools, APIs, and libraries.
    Return ONLY a valid JSON object matching this schema strictly, with no markdown formatting or extra text:
    {{
        "skills": ["python", "react", "postgresql", ...]
    }}

    Job Descriptions:
    {text}
    """

    payload = {
        "model": model,
        "max_tokens": 1500,
        "messages": [
            {"role": "system", "content": "You are a data extraction assistant that strictly outputs valid JSON. Do not output any conversational text or markdown code blocks."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(base_url, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise LLMClientError(f"Error from LLM API: {response.text}")
        
    try:
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        data = json.loads(content)
        validated = SkillExtraction(**data)
        
        # Normalize and filter
        skills = [skill.lower().strip() for skill in validated.skills]
        return list(set(skills)) # Deduplicate initially
    except Exception as e:
        raise LLMClientError(f"Failed to parse LLM response: {e}. Raw content: {content}")
