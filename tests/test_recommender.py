import pandas as pd
from src.career_recommender import recommend_careers
from src.skill_gap_analyzer import analyze_skill_gap
from src.roadmap_planner import build_roadmap

def test_recommender_returns_ranked_rows():
    careers = pd.DataFrame([
        {"career_id": "1", "title": "Data Analyst", "description": "Analyze data", "skills": "python;sql;statistics", "interests": "analytics;problem solving"},
        {"career_id": "2", "title": "Frontend Developer", "description": "Build interfaces", "skills": "html;css;javascript", "interests": "design;creativity"},
    ])
    profile = {"skills": ["python", "sql"], "interests": ["analytics"], "education": "B.Tech", "goal": "data"}
    result = recommend_careers(profile, careers, top_k=2)
    assert len(result) == 2
    assert result.iloc[0]["title"] == "Data Analyst"
    assert 0 <= result.iloc[0]["score"] <= 100

def test_skill_gap_coverage():
    gap = analyze_skill_gap(["python", "sql"], ["python", "sql", "statistics"])
    assert gap["matched"] == ["python", "sql"]
    assert gap["missing"] == ["statistics"]
    assert gap["coverage"] == 66.7

def test_roadmap_for_missing_skill():
    resources = pd.DataFrame([{"title": "SQLBolt", "provider": "SQLBolt", "skills": "sql", "url": "https://sqlbolt.com/", "estimated_hours": 6}])
    roadmap = build_roadmap(["sql"], resources, weeks=4)
    assert len(roadmap) == 1
    assert roadmap.iloc[0]["skill"] == "sql"
    assert roadmap.iloc[0]["url"] == "https://sqlbolt.com/"
