import os
import sys

import streamlit as st


# Ensure src is importable when running `streamlit run ui/app.py`
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.main import load_syllabus, query_topics  # noqa: E402


st.set_page_config(page_title="StudySpark Buildathon", page_icon="📚", layout="wide")
st.title("📚 StudySpark: CBSE STEM Explorer")
st.caption("Search syllabus topics and get a guided study plan.")

with st.sidebar:
    st.header("Filters")
    subject = st.selectbox("Subject", ["", "Math", "Science"], index=0)
    grade = st.selectbox("Grade", ["", 6, 7, 8, 9, 10], index=0)
    grade_val = None if grade == "" else int(grade)

query = st.text_input("What do you want to study?", placeholder="e.g., linear equations basics")
run = st.button("Find Topics")

with st.expander("View syllabus data", expanded=False):
    df = load_syllabus()
    st.dataframe(df, use_container_width=True)

if run and query.strip():
    with st.spinner("Thinking..."):
        result = query_topics(query.strip(), subject or None, grade_val)
    st.subheader("Suggested Topics")
    if result["matches"]:
        for m in result["matches"][:5]:
            st.write(f"- {m['subject']} G{m['grade']}: {m['topic']} ({m['keywords']})")
    else:
        st.info("No direct matches. Showing a generic plan.")

    st.subheader("Study Plan")
    st.write(result["answer"])
else:
    st.info("Enter a query and click 'Find Topics' to get started.")


