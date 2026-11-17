from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv_fallback import load_local_env

from database.db import init_db, save_profile, replace_roadmap, get_tasks, set_task_completed
from src.career_recommender import recommend_careers, split_skills, normalise_skill
from src.resume_parser import extract_pdf_text, extract_skills
from src.skill_gap_analyzer import analyze_skill_gap
from src.roadmap_planner import build_roadmap
from src.career_assistant import build_knowledge_base, answer_question

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
load_local_env(ROOT / ".env")
st.set_page_config(page_title="Autonomous Career Navigation Agent", page_icon="🧭", layout="wide")
init_db()

@st.cache_data
def load_data():
    careers = pd.read_csv(DATA / "careers.csv").fillna("")
    resources = pd.read_csv(DATA / "learning_resources.csv").fillna("")
    return careers, resources

careers, resources = load_data()
knowledge_docs = build_knowledge_base(careers, resources)

st.title("🧭 Autonomous Career Navigation Agent")
st.caption("A student-focused career planning prototype using transparent ML matching, skill-gap analysis, curated learning resources and optional LLM assistance.")

with st.sidebar:
    st.header("Student profile")
    name = st.text_input("Your name", value="Student")
    education = st.selectbox("Education", ["B.Tech CSE / AI", "B.Tech other branch", "BCA", "MCA", "B.Sc.", "M.Sc.", "Other"])
    raw_skills = st.text_area("Current skills (comma-separated)", "python, sql, machine learning, pandas, git")
    raw_interests = st.text_area("Interests (comma-separated)", "artificial intelligence, analytics, problem solving")
    goal = st.text_input("Career goal (optional)", "Build a career in AI")
    projects = st.text_area("Projects / experience (optional)", "")
    uploaded_resume = st.file_uploader("Or upload a text-based PDF resume", type=["pdf"])
    if uploaded_resume:
        if st.button("Extract skills from resume"):
            try:
                resume_text = extract_pdf_text(uploaded_resume)
                found = extract_skills(resume_text)
                if found:
                    st.session_state["resume_skills"] = found
                    st.success(f"Detected {len(found)} skills. Review them before using.")
                else:
                    st.warning("No known skills were detected. You can enter skills manually.")
            except Exception as exc:
                st.error(f"Could not read the PDF: {exc}")
    if "resume_skills" in st.session_state:
        st.caption("Detected skills: " + ", ".join(st.session_state["resume_skills"]))
        if st.button("Use detected skills"):
            raw_skills = ", ".join(st.session_state["resume_skills"])
            st.session_state["skills_override"] = raw_skills

if "skills_override" in st.session_state:
    raw_skills = st.session_state["skills_override"]

def parse_csv_input(value: str) -> list[str]:
    return [normalise_skill(x) for x in value.split(",") if x.strip()]

profile = {
    "name": name.strip() or "Student",
    "education": education,
    "skills": parse_csv_input(raw_skills),
    "interests": parse_csv_input(raw_interests),
    "goal": goal,
    "projects": projects,
}

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Career Matches", "Skill Gap", "Learning Roadmap", "Career Assistant", "Progress"
])

with tab1:
    st.subheader("Recommended career paths")
    st.write("Scores are relative matches within this demo dataset—not probabilities of employment or guarantees.")
    top_k = st.slider("Number of careers to show", min_value=3, max_value=10, value=5)
    results = recommend_careers(profile, careers, top_k=top_k)
    if results.empty:
        st.info("Add your skills and interests in the sidebar to get started.")
    else:
        for _, row in results.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"### {row['title']}")
                c1.write(row["description"])
                c1.caption("Matched skills: " + (", ".join(row["matched_skills"]) or "None detected yet"))
                c2.metric("Match score", f"{row['score']:.1f}/100")
                if row["missing_skills"]:
                    st.caption("Potential skills to develop: " + ", ".join(row["missing_skills"][:8]))
                if st.button("Build roadmap for " + str(row["title"]), key="roadmap_" + str(row["career_id"])):
                    st.session_state["selected_career_id"] = row["career_id"]
                    st.session_state["selected_career_title"] = row["title"]
                    gap = analyze_skill_gap(profile["skills"], row["required_skills"])
                    roadmap = build_roadmap(gap["missing"], resources, weeks=6)
                    replace_roadmap(profile["name"], row["title"], roadmap)
                    save_profile(profile)
                    st.session_state["roadmap_created"] = True
                    st.success(f"Roadmap created for {row['title']}. Open the Learning Roadmap tab.")

with tab2:
    st.subheader("Skill-gap analysis")
    career_choice = st.selectbox("Choose a target role", careers["title"].tolist(), key="gap_career")
    career = careers.loc[careers["title"] == career_choice].iloc[0]
    gap = analyze_skill_gap(profile["skills"], career["skills"])
    a, b, c = st.columns(3)
    a.metric("Skill coverage", f"{gap['coverage']}%")
    b.metric("Skills matched", len(gap["matched"]))
    c.metric("Skills to develop", len(gap["missing"]))
    st.progress(int(gap["coverage"]))
    left, right = st.columns(2)
    with left:
        st.markdown("**Skills you already have**")
        st.write(", ".join(gap["matched"]) if gap["matched"] else "No matching skills detected yet.")
    with right:
        st.markdown("**Potential gaps**")
        st.write(", ".join(gap["missing"]) if gap["missing"] else "No gaps found in this role's listed skills.")
    st.caption("This analysis is based on the role's sample skill list. Validate requirements against current job descriptions.")

with tab3:
    st.subheader("Personalized learning roadmap")
    if st.button("Generate roadmap for selected role"):
        career_choice = st.session_state.get("gap_career", careers.iloc[0]["title"])
        career = careers.loc[careers["title"] == career_choice].iloc[0]
        gap = analyze_skill_gap(profile["skills"], career["skills"])
        roadmap = build_roadmap(gap["missing"], resources, weeks=6)
        replace_roadmap(profile["name"], career_choice, roadmap)
        save_profile(profile)
        st.session_state["selected_career_title"] = career_choice
        st.session_state["roadmap_created"] = True
    tasks = get_tasks(profile["name"])
    if tasks:
        task_df = pd.DataFrame([dict(t) for t in tasks])
        st.info(f"Roadmap for: {task_df.iloc[0]['career_title']}")
        for _, task in task_df.iterrows():
            label = f"Week {task['week']}: {task['task']} — resource: {task['resource']}"
            checked = st.checkbox(label, value=bool(task["completed"]), key=f"task_{task['id']}")
            if checked != bool(task["completed"]):
                set_task_completed(int(task["id"]), checked)
                st.rerun()
            if task["url"]:
                st.markdown(f"[Open resource]({task['url']})")
        refreshed = pd.DataFrame([dict(t) for t in get_tasks(profile["name"])])
        completed = int(refreshed["completed"].sum()) if not refreshed.empty else 0
        st.metric("Roadmap completion", f"{completed}/{len(refreshed)} tasks")
        if not refreshed.empty:
            st.plotly_chart(px.bar(refreshed, x="skill", y="week", color="completed",
                                   title="Roadmap tasks by week"), use_container_width=True)
    else:
        st.write("No roadmap saved for this profile yet. Create one from Career Matches or Skill Gap.")

with tab4:
    st.subheader("Career Assistant")
    st.write("Answers are grounded in the local career and resource catalogue. Optional Gemini generation can be enabled with an API key.")
    question = st.text_input("Ask about a career, missing skills, or learning resources",
                             placeholder="What should I learn for an entry-level data analyst role?")
    use_llm = st.checkbox("Use Gemini API if configured", value=False)
    if st.button("Get guidance", type="primary"):
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            result = answer_question(question.strip(), knowledge_docs, use_gemini=use_llm)
            st.caption("Mode: " + result["mode"])
            st.markdown(result["answer"])
            if result["sources"]:
                with st.expander("Retrieved source records"):
                    for source in result["sources"]:
                        st.markdown(f"- **{source['title']}** — {source['source']} (retrieval score: {source['retrieval_score']})")

with tab5:
    st.subheader("Progress overview")
    tasks = get_tasks(profile["name"])
    if tasks:
        task_df = pd.DataFrame([dict(t) for t in tasks])
        total = len(task_df)
        completed = int(task_df["completed"].sum())
        c1, c2, c3 = st.columns(3)
        c1.metric("Total tasks", total)
        c2.metric("Completed", completed)
        c3.metric("Completion", f"{100 * completed / max(1, total):.0f}%")
        st.dataframe(task_df[["week", "skill", "task", "resource", "completed"]], use_container_width=True, hide_index=True)
        st.write("As tasks are completed, use Skill Gap and Career Matches again to refresh the roadmap when your skills or goals change.")
    else:
        st.info("Create a learning roadmap to begin tracking progress.")

with st.expander("About the prototype, data and limitations"):
    st.markdown("""
    - Career roles and learning resources are a small, curated starter catalogue included with the project.
    - Career matching uses TF-IDF text similarity plus explicit skill and interest overlap. Scores are ranking aids, not job probabilities.
    - Resume skill detection is dictionary-based and can miss synonyms, context, or skills listed in unusual formats.
    - The local assistant retrieves relevant records using TF-IDF. Gemini generation is optional and requires your own API key.
    - This is a student decision-support prototype, not a guarantee of employability. Verify current job descriptions, course availability, fees, and prerequisites.
    """)

st.divider()
st.caption("Autonomous Career Navigation Agent • Final-year project prototype")
