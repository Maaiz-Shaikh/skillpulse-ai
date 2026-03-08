from pydantic import BaseModel, Field

class SkillExtraction(BaseModel):
    skills: list[str] = Field(description="A list of technical skills (e.g., programming languages, frameworks, databases, cloud platforms, DevOps tools) extracted from the job descriptions. Normalize them to lowercase and standard names.")
