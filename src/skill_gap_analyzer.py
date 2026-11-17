"""Skill coverage and gap analysis utilities."""
from __future__ import annotations
from src.career_recommender import split_skills, normalise_skill

def analyze_skill_gap(user_skills: list[str], required_skills: list[str] | str) -> dict:
    user = {normalise_skill(x) for x in user_skills if str(x).strip()}
    required = set(split_skills(required_skills) if isinstance(required_skills, str) else
                   [normalise_skill(x) for x in required_skills if str(x).strip()])
    matched = sorted(user & required)
    missing = sorted(required - user)
    coverage = round(100 * len(matched) / max(1, len(required)), 1)
    return {"matched": matched, "missing": missing, "required": sorted(required), "coverage": coverage}
