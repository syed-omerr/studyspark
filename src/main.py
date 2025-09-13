import os
from typing import List, Dict

import pandas as pd

from .agents import get_simple_agent


DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cbse_stem.csv")


def ensure_data_exists() -> None:
    """Create a minimal CSV if it does not exist so the app can run immediately."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(
            [
                {"subject": "Math", "grade": 8, "topic": "Algebra Basics", "keywords": "variables, expressions"},
                {"subject": "Math", "grade": 8, "topic": "Linear Equations", "keywords": "slope, intercept"},
                {"subject": "Science", "grade": 8, "topic": "Atoms and Molecules", "keywords": "proton, neutron, electron"},
                {"subject": "Science", "grade": 8, "topic": "Force and Motion", "keywords": "force, inertia, acceleration"},
            ]
        )
        df.to_csv(DATA_PATH, index=False)


def load_syllabus() -> pd.DataFrame:
    """Load the syllabus CSV into a DataFrame."""
    ensure_data_exists()
    return pd.read_csv(DATA_PATH)


def filter_topics(df: pd.DataFrame, subject: str | None = None, grade: int | None = None) -> pd.DataFrame:
    """Filter topics by optional subject and grade."""
    filtered = df
    if subject:
        filtered = filtered[filtered["subject"].str.lower() == subject.lower()]
    if grade is not None:
        filtered = filtered[filtered["grade"] == grade]
    return filtered.reset_index(drop=True)


def query_topics(question: str, subject: str | None = None, grade: int | None = None) -> Dict[str, List[Dict[str, str]]]:
    """Simple query that returns matching topics and an agent response."""
    df = load_syllabus()
    subset = filter_topics(df, subject, grade)

    # naive match: keyword containment
    matches = []
    lower_q = question.lower()
    for _, row in subset.iterrows():
        text = f"{row['topic']} {row.get('keywords', '')}"
        if any(token in text.lower() for token in lower_q.split()):
            matches.append({
                "subject": str(row["subject"]),
                "grade": str(row["grade"]),
                "topic": str(row["topic"]),
                "keywords": str(row.get("keywords", "")),
            })

    agent = get_simple_agent()
    context = "\n".join(f"- {m['subject']} G{m['grade']}: {m['topic']} ({m['keywords']})" for m in matches[:10])
    prompt = (
        "You are a helpful curriculum assistant. Given the student's question and a list of syllabus topics, "
        "suggest 3 relevant topics and a brief study plan. Use only the provided context.\n\n"
        f"Question: {question}\n\nContext:\n{context if context else 'No matching topics found.'}"
    )
    answer = agent(prompt)

    return {"matches": matches, "answer": answer}


__all__ = [
    "load_syllabus",
    "filter_topics",
    "query_topics",
]


