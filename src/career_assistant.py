"""Lightweight retrieval-based career assistant with optional Gemini generation."""
from __future__ import annotations
import os
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_knowledge_base(careers: pd.DataFrame, resources: pd.DataFrame) -> list[dict]:
    docs = []
    for _, row in careers.iterrows():
        docs.append({
            "title": f"Career role: {row.get('title', '')}",
            "text": f"Role: {row.get('title', '')}\nDescription: {row.get('description', '')}\nSkills: {str(row.get('skills', '')).replace(';', ', ')}\nInterests: {str(row.get('interests', '')).replace(';', ', ')}",
            "source": f"Local career catalogue ({row.get('career_id', '')})",
        })
    for _, row in resources.iterrows():
        docs.append({
            "title": f"Learning resource: {row.get('title', '')}",
            "text": f"Resource: {row.get('title', '')}\nProvider: {row.get('provider', '')}\nSkills: {str(row.get('skills', '')).replace(';', ', ')}\nType: {row.get('resource_type', '')}\nEstimated hours: {row.get('estimated_hours', '')}",
            "source": str(row.get("url", "")),
        })
    return docs

def retrieve_context(question: str, docs: list[dict], top_k: int = 3) -> list[dict]:
    if not docs:
        return []
    corpus = [d["text"] for d in docs] + [question]
    matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform(corpus)
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    indices = scores.argsort()[::-1][:max(1, top_k)]
    return [dict(docs[i], retrieval_score=round(float(scores[i]), 3)) for i in indices if scores[i] > 0]

def answer_question(question: str, docs: list[dict], use_gemini: bool = False) -> dict:
    context = retrieve_context(question, docs)
    if not context:
        return {
            "answer": "I couldn't find a close match in the local career knowledge base. Try asking about a specific role, skill, or learning resource.",
            "sources": [],
            "mode": "Local retrieval",
        }
    context_text = "\n\n".join(f"[{i+1}] {d['text']}\nSource: {d['source']}" for i, d in enumerate(context))
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if use_gemini and api_key:
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash").strip()
        prompt = (
            "You are a careful career-planning assistant. Answer only using the supplied context. "
            "If the context does not contain an answer, say what is missing. Do not promise employment. "
            "Give practical, concise advice and cite context as [1], [2], etc.\n\n"
            f"Context:\n{context_text}\n\nQuestion: {question}"
        )
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                params={"key": api_key},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700}},
                timeout=25,
            )
            response.raise_for_status()
            payload = response.json()
            answer = payload["candidates"][0]["content"]["parts"][0]["text"]
            return {"answer": answer, "sources": context, "mode": "Gemini + local retrieval"}
        except Exception:
            # Fail safely to the local answer if the API is unavailable or the key is invalid.
            pass
    bullets = "\n".join(
        f"- **{d['title']}** — {d['text'].replace(chr(10), ' | ')} (Source: {d['source']})"
        for d in context
    )
    return {
        "answer": "Here is the most relevant information in the local knowledge base:\n\n" + bullets +
                  "\n\nUse these results as a starting point and verify course details and role requirements before making decisions.",
        "sources": context,
        "mode": "Local retrieval",
    }
