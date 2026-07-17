"""
AI Mock Interview Coach
-----------------------
Streamlit app that takes a job description (+ optional resume text),
generates tailored interview questions with Gemini, scores the user's
typed answers, gives actionable feedback, and produces a final
readiness report.

Run:
    streamlit run app.py
"""

import streamlit as st
from utils import generate_questions, evaluate_answer, build_final_report

st.set_page_config(page_title="AI Mock Interview Coach", page_icon="🎤", layout="centered")

# ---------------------------------------------------------------- session state
defaults = {
    "stage": "setup",       # setup -> interview -> report
    "questions": [],
    "current_idx": 0,
    "evaluations": [],
    "job_title": "",
    "job_description": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def reset_app():
    for key, val in defaults.items():
        st.session_state[key] = val


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Setup")
    api_key = st.text_input("Gemini API key", type="password", help="Get one free at aistudio.google.com/apikey")
    st.caption("Your key is used only for this session and never stored.")
    st.divider()
    if st.button("🔄 Restart session"):
        reset_app()
        st.rerun()

st.title("🎤 AI Mock Interview Coach")
st.caption("Paste a job description, answer tailored questions, get scored feedback.")

# ---------------------------------------------------------------- STAGE 1: setup
if st.session_state.stage == "setup":
    job_title = st.text_input("Job title you're preparing for", placeholder="e.g. Generative AI Intern")
    job_description = st.text_area(
        "Paste the job description",
        height=180,
        placeholder="Paste the JD text here...",
    )
    resume_text = st.text_area(
        "Optional: paste your resume text (improves question targeting)",
        height=120,
        placeholder="Paste resume text here (optional)...",
    )
    num_questions = st.slider("Number of questions", min_value=3, max_value=10, value=6)

    if st.button("Generate interview ➜", type="primary"):
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif not job_description.strip():
            st.error("Please paste a job description.")
        else:
            with st.spinner("Generating tailored questions..."):
                try:
                    questions = generate_questions(api_key, job_description, resume_text, num_questions)
                    st.session_state.questions = questions
                    st.session_state.job_title = job_title or "this role"
                    st.session_state.job_description = job_description
                    st.session_state.evaluations = []
                    st.session_state.current_idx = 0
                    st.session_state.stage = "interview"
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't generate questions: {e}")

# ---------------------------------------------------------------- STAGE 2: interview
elif st.session_state.stage == "interview":
    idx = st.session_state.current_idx
    questions = st.session_state.questions
    total = len(questions)

    st.progress(idx / total, text=f"Question {idx + 1} of {total}")
    q = questions[idx]
    st.subheader(f"{'🧠 Technical' if q['type'] == 'technical' else '💬 Behavioral'}")
    st.write(f"**{q['question']}**")

    answer = st.text_area("Your answer", height=150, key=f"answer_{q['id']}")

    col1, col2 = st.columns([1, 1])
    with col1:
        submit = st.button("Submit answer ➜", type="primary", use_container_width=True)
    with col2:
        skip = st.button("Skip question", use_container_width=True)

    if submit or skip:
        if submit and not answer.strip():
            st.warning("Type an answer, or use Skip.")
        else:
            with st.spinner("Evaluating your answer..."):
                try:
                    eval_result = evaluate_answer(
                        api_key,
                        q["question"],
                        q["type"],
                        answer if submit else "(skipped)",
                        st.session_state.job_description,
                    )
                    eval_result["question"] = q["question"]
                    eval_result["type"] = q["type"]
                    eval_result["answer"] = answer if submit else "(skipped)"
                    st.session_state.evaluations.append(eval_result)

                    if idx + 1 < total:
                        st.session_state.current_idx += 1
                    else:
                        st.session_state.stage = "report"
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't evaluate answer: {e}")

# ---------------------------------------------------------------- STAGE 3: report
elif st.session_state.stage == "report":
    st.header("📊 Your Interview Readiness Report")
    report = build_final_report(st.session_state.evaluations, st.session_state.job_title)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall", f"{report['overall_score']}/10")
    c2.metric("Relevance", f"{report['avg_relevance']}/10")
    c3.metric("Clarity", f"{report['avg_clarity']}/10")
    c4.metric("Depth", f"{report['avg_depth']}/10")

    st.info(report["readiness"])

    st.divider()
    st.subheader("Question-by-question breakdown")
    for i, e in enumerate(st.session_state.evaluations, start=1):
        with st.expander(f"Q{i}: {e['question'][:70]}{'...' if len(e['question']) > 70 else ''}"):
            st.write(f"**Your answer:** {e['answer']}")
            st.write(f"Relevance **{e['relevance_score']}/10** · Clarity **{e['clarity_score']}/10** · Depth **{e['depth_score']}/10**")
            st.success(f"✅ Strengths: {e['strengths']}")
            st.warning(f"🔧 Improve: {e['improvements']}")
            st.write(f"**Sample strong answer:** {e['model_answer']}")

    st.divider()
    if st.button("🔁 Practice again"):
        reset_app()
        st.rerun()
