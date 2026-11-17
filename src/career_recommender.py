"""Transparent baseline career recommender using TF-IDF and weighted profile matching."""
from __future__ import annotations

import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def split_skills(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, float) and pd.isna(value):
        return []
    return [normalise_skill(x) for x in str(value).split(";") if x.strip()]

def normalise_skill(value: str) -> str:
    value = str(value).strip().lower()
    value = re.sub(r"\s+", " ", value)
    aliases = {
        "ml": "machine learning",
        "powerbi": "power bi",
        "js": "javascript",
        "natural language processing": "nlp",
        "retrieval augmented generation": "rag",
        "large language models": "llm",
    }
    return aliases.get(value, value)

def profile_document(profile: dict) -> str:
    parts = [
        " ".join(profile.get("skills", [])),
        " ".join(profile.get("interests", [])),
        str(profile.get("education", "")),
        str(profile.get("projects", "")),
        str(profile.get("goal", "")),
    ]
    return " ".join(parts).lower()

def recommend_careers(profile: dict, careers: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    """Rank career options. Scores are relative matching scores, not job probability."""
    if careers.empty:
        return pd.DataFrame(columns=["career_id", "title", "score", "matched_skills", "missing_skills", "description"])
    user_skills = {normalise_skill(s) for s in profile.get("skills", []) if str(s).strip()}
    user_interests = {normalise_skill(s) for s in profile.get("interests", []) if str(s).strip()}
    user_text = profile_document(profile)

    career_docs = (
        careers["title"].fillna("").astype(str) + " " +
        careers["description"].fillna("").astype(str) + " " +
        careers["skills"].fillna("").astype(str).str.replace(";", " ", regex=False) + " " +
        careers["interests"].fillna("").astype(str).str.replace(";", " ", regex=False)
    ).tolist()
    corpus = career_docs + [user_text or "student exploring careers"]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(corpus)
    semantic_scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()

    rows = []
    for idx, (_, career) in enumerate(careers.iterrows()):
        required = set(split_skills(career.get("skills", "")))
        career_interests = set(split_skills(career.get("interests", "")))
        matched = sorted(user_skills & required)
        missing = sorted(required - user_skills)
        skill_score = len(matched) / max(1, len(required))
        interest_score = len(user_interests & career_interests) / max(1, len(career_interests))
        # A transparent weighted score; semantic matching helps when text overlaps but exact skills do not.
        score = 100 * (0.55 * skill_score + 0.20 * interest_score + 0.25 * float(semantic_scores[idx]))
        rows.append({
            "career_id": career.get("career_id", ""),
            "title": career.get("title", "Unknown"),
            "score": round(float(score), 1),
            "matched_skills": matched,
            "missing_skills": missing,
            "description": career.get("description", ""),
            "required_skills": sorted(required),
        })
    result = pd.DataFrame(rows).sort_values(["score", "title"], ascending=[False, True])
    return result.head(max(1, int(top_k))).reset_index(drop=True)
