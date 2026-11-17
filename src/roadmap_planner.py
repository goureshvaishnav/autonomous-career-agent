"""Rule-based roadmap generator grounded in the curated learning_resources.csv catalogue."""
from __future__ import annotations
import pandas as pd
from src.career_recommender import split_skills, normalise_skill

def build_roadmap(missing_skills: list[str], resources: pd.DataFrame, weeks: int = 6) -> pd.DataFrame:
    weeks = max(1, min(int(weeks), 24))
    if not missing_skills:
        return pd.DataFrame(columns=["week", "skill", "task", "resource", "provider", "url", "estimated_hours"])
    rows = []
    for i, skill in enumerate(missing_skills):
        candidates = []
        for _, resource in resources.iterrows():
            resource_skills = split_skills(resource.get("skills", ""))
            if normalise_skill(skill) in resource_skills:
                candidates.append(resource)
        if candidates:
            resource = candidates[0]
            title, provider, url = resource["title"], resource["provider"], resource["url"]
            hours = int(float(resource.get("estimated_hours", 4)))
        else:
            title, provider, url, hours = "Create a small practice project", "Self-directed practice", "", 4
        week = min(weeks, (i % weeks) + 1)
        rows.append({
            "week": week,
            "skill": skill,
            "task": f"Learn {skill} fundamentals and complete one practical exercise",
            "resource": title,
            "provider": provider,
            "url": url,
            "estimated_hours": hours,
        })
    return pd.DataFrame(rows).sort_values(["week", "skill"]).reset_index(drop=True)
