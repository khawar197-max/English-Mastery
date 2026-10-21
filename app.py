import streamlit as st
from modules.db import init_db, save_attempt, get_stats, get_recent_attempts, save_writing, get_writings
from modules.vocabulary import load_words, make_vocab_question
from modules.grammar import GRAMMAR_QUESTIONS
from modules.examiner import assess_writing
from modules.duplicates import normalize_text, find_duplicate

st.set_page_config(page_title="English Mastery", page_icon="📚", layout="wide")
init_db()

st.title("📚 English Mastery")
st.caption("GRE vocabulary • FPSC/SPSC English • Grammar • Precis • Essay practice")
st.info("Practice feedback only. Scores are estimates against the app's learning rubrics, not official FPSC/SPSC marks.")

words = load_words()
pages = ["Dashboard", "Vocabulary", "Grammar MCQs", "Precis Practice", "Essay Practice", "My History"]
page = st.sidebar.radio("Choose a module", pages)

stats = get_stats()
if page == "Dashboard":
    st.subheader("Your learning dashboard")
    c1, c2, c3 = st.columns(3)
    c1.metric("Objective attempts", stats["objective_attempts"])
    c2.metric("Correct answers", stats["correct_answers"])
    c3.metric("Writing submissions", stats["writing_submissions"])
    st.markdown("### Suggested study routine")
    st.markdown("- **15 minutes:** learn 5–10 new words and review difficult words.\n- **10 minutes:** complete grammar MCQs and read explanations.\n- **20–30 minutes:** practise precis or essay writing several times a week.")
    st.markdown("### What is saved?")
    st.write("Your attempts and writing submissions are stored in a local SQLite database (`english_mastery.db`). Keep a backup, especially before moving or redeploying the app.")

elif page == "Vocabulary":
    st.subheader("Vocabulary practice")
    st.write(f"Loaded **{len(words)}** starter words. Add more to `data/vocabulary.json` as you grow your study bank.")
    if "vocab_q" not in st.session_state:
        st.session_state.vocab_q = make_vocab_question(words)
    q = st.session_state.vocab_q
    st.markdown(f"**Word:** `{q['word']}`")
    st.write(q["prompt"])
    choice = st.radio("Choose the closest meaning", q["options"], key="vocab_choice")
    if st.button("Check answer", key="vocab_check"):
        correct = choice == q["answer"]
        save_attempt("vocabulary", q["word"], choice, q["answer"], 1 if correct else 0, 1,
                     q.get("explanation", ""))
        if correct:
            st.success("Correct! +1 mark")
        else:
            st.error(f"Not quite. Correct answer: **{q['answer']}**")
        if q.get("explanation"):
            st.caption(q["explanation"])
    if st.button("Next vocabulary question"):
        st.session_state.vocab_q = make_vocab_question(words)
        st.rerun()

elif page == "Grammar MCQs":
    st.subheader("Grammar and usage")
    q = st.selectbox("Select a practice question", GRAMMAR_QUESTIONS, format_func=lambda x: x["question"])
    choice = st.radio("Choose one answer", q["options"], key="grammar_choice")
    if st.button("Check grammar answer"):
        correct = choice == q["answer"]
        save_attempt("grammar", q["question"], choice, q["answer"], 1 if correct else 0, 1, q["explanation"])
        if correct:
            st.success("Correct! +1 mark")
        else:
            st.error(f"Correct answer: **{q['answer']}**")
        st.write(q["explanation"])

elif page in ["Precis Practice", "Essay Practice"]:
    is_essay = page == "Essay Practice"
    st.subheader("Essay practice" if is_essay else "Precis practice")
    if is_essay:
        prompt = st.text_area("Essay topic", placeholder="e.g., Good governance is essential for sustainable development.", height=80)
        text = st.text_area("Write your essay", placeholder="Write your complete essay here...", height=300)
        max_marks = 100
        rubric = {
            "Topic relevance and thesis": 20,
            "Arguments and analysis": 25,
            "Organization and coherence": 20,
            "Evidence and examples": 15,
            "Grammar and sentence structure": 10,
            "Vocabulary, style and clarity": 10,
        }
    else:
        prompt = st.text_area("Source passage", placeholder="Paste a passage here, or write your own practice passage.", height=180)
        text = st.text_area("Write your precis", placeholder="Write a concise precis in your own words...", height=180)
        max_marks = 20
        rubric = {
            "Central idea": 5,
            "Conciseness and length": 4,
            "Grammar and sentence structure": 4,
            "Coherence and logical flow": 4,
            "Title": 3,
        }

    st.caption("For the most useful feedback, provide the original passage for precis. The built-in evaluator uses transparent heuristic checks; it is not a substitute for a human examiner or an AI model.")
    if st.button("Assess my writing", type="primary"):
        if not text.strip():
            st.warning("Please enter your writing first.")
        else:
            result = assess_writing(text, prompt, is_essay=is_essay, rubric=rubric)
            save_writing("essay" if is_essay else "precis", prompt, text, result["score"], max_marks, result["feedback"])
            st.metric("Practice score", f"{result['score']} / {max_marks}")
            st.markdown("### Feedback")
            for item in result["feedback"]:
                st.write(f"- {item}")
            st.markdown("### Rubric used")
            for criterion, marks in rubric.items():
                st.write(f"- {criterion}: up to {marks} marks")
            st.warning("This is a preliminary, rule-based practice score. It does not claim to reproduce official exam marking.")

elif page == "My History":
    st.subheader("Your saved learning history")
    recent = get_recent_attempts(50)
    if not recent:
        st.write("No objective attempts saved yet. Try Vocabulary or Grammar MCQs first.")
    else:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    st.markdown("### Writing submissions")
    writings = get_writings(20)
    if not writings:
        st.write("No writing submissions saved yet.")
    else:
        st.dataframe(writings, use_container_width=True, hide_index=True)

st.sidebar.divider()
st.sidebar.caption("MVP v0.1 • Local-first • No paid services required for basic practice")
