# Project plan and final-year scope

## Problem statement
Students often struggle to connect their current skills and interests with realistic career paths and actionable learning plans. Generic recommendation lists do not always explain skill gaps or adapt to progress.

## Objectives
1. Recommend and rank career roles from student-provided information.
2. Explain recommendations using skill overlap and text similarity.
3. Compare student skills with role requirements.
4. Generate a roadmap using a curated resource catalogue.
5. Track completion and allow the student to regenerate the plan.
6. Provide grounded career Q&A using retrieval and optional LLM generation.
7. Evaluate recommendations against a baseline and document limitations.

## Proposed modules
- Student profile manager
- Resume text extraction and skill detection
- Career recommendation engine
- Skill-gap analyzer
- Learning roadmap planner
- Career assistant (retrieval + optional Gemini)
- Progress tracker (SQLite)

## Research / evaluation plan
- Prepare an anonymized test set of 20–50 student-like profiles with expected relevant roles.
- Compare the hybrid ranking to a simple keyword-overlap baseline.
- Report Precision@3, Recall@3, and qualitative relevance review where labels are available.
- Manually review skill-gap results against the role catalogue.
- Measure task completion and gather brief usability feedback from volunteer testers.
- Record dataset construction, scoring weights, known biases and failure cases.

## Known limitations and future work
- Expand and source the role catalogue from public occupational frameworks and real job descriptions.
- Add a consent-based live job feed with source URLs and retrieval timestamps.
- Add robust resume parsing and synonym-aware skill extraction.
- Add student authentication and data export/deletion.
- Add controlled evaluation of adaptive roadmap updates.
- Conduct a fairness review across education backgrounds and nontraditional paths.
