# Autonomous Career Navigation Agent

A lightweight final-year B.Tech AI project prototype for personalized career exploration. It combines a transparent ML career-ranking baseline, skill-gap analysis, curated learning-roadmap generation, progress tracking, PDF resume skill extraction, and a local retrieval-based career assistant with optional Gemini API generation.

## Features

- Student profile: education, skills, interests, goals and projects
- Career matching: TF-IDF semantic similarity + skill overlap + interest overlap
- Explainability: matched skills, missing skills, and relative match score
- PDF resume parsing using PyMuPDF and dictionary-based skill detection
- Skill-gap analysis against the role catalogue
- Learning roadmap based on curated resources
- SQLite progress tracking
- Local retrieval-based career Q&A
- Optional Gemini API response generation, with local fallback
- Pytest tests for the main algorithmic components

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 recommended (Python 3.13 may work depending on installed wheels)
- VS Code

## Setup (PowerShell)

Open PowerShell in the project directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, run this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If Python 3.12 is not installed, use `py -m venv .venv` with your installed Python and proceed.

## Run the app

```powershell
python -m streamlit run app.py
```

Streamlit will show a local URL, usually `http://localhost:8501`. Open it in your browser.

## Run tests

```powershell
python -m pytest -q
```

## Optional Gemini setup

1. Copy `.env.example` to `.env`.
2. Add your own Gemini API key to `.env` as `GEMINI_API_KEY=your_key_here`.
3. Keep `.env` private; it is included in `.gitignore`.
4. In Career Assistant, select "Use Gemini API if configured".

Without an API key, the application still runs using local TF-IDF retrieval. The API is optional and may have quota, availability, or pricing limits. Confirm the current terms and model availability with Google before use.

## Project layout

```text
autonomous-career-agent/
├── app.py
├── requirements.txt
├── data/
│   ├── careers.csv
│   └── learning_resources.csv
├── src/
│   ├── career_recommender.py
│   ├── resume_parser.py
│   ├── skill_gap_analyzer.py
│   ├── roadmap_planner.py
│   └── career_assistant.py
├── database/
│   └── db.py
└── tests/
    └── test_recommender.py
```

## How the recommendation score works

The baseline score is a weighted combination:

- 55% exact required-skill coverage
- 20% interest overlap
- 25% TF-IDF text similarity

This weighting is a design choice for the prototype, not a scientifically validated model. In your report, document it and compare it against a simple keyword baseline using a small, clearly described evaluation set.

## Suggested final-year evaluation

Create 20–50 anonymized or synthetic student profiles with expected top career categories. Compare the recommender with a keyword-overlap baseline using Precision@K / Recall@K or expert-reviewed relevance ratings. Evaluate skill-gap detection against manually labeled skill requirements. Report limitations, data sources, and reproducibility details. Do not claim that synthetic evaluation proves real-world employment outcomes.

## Important limitations

- Included roles and learning resources are starter data, not a complete live job-market feed.
- No job openings are fetched live in this version.
- Resume skill detection uses known phrases and can miss synonyms or context.
- Match scores are relative ranking aids, not employment probabilities.
- Career recommendations should support, not replace, a student's own judgment or qualified career guidance.
