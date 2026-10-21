# English Mastery — MVP v0.1

A local-first Streamlit practice app for GRE vocabulary and FPSC/SPSC-style English preparation.

## Features in this starter
- Vocabulary multiple-choice practice
- Grammar MCQs with explanations
- Precis and essay practice submission
- Transparent, heuristic practice feedback
- Local SQLite history for objective attempts and writing submissions
- Basic exact-text normalization to avoid duplicate question-bank entries

## Requirements
- Python 3.10 or newer
- Internet connection only to install Streamlit

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Where your data is saved
The app creates `english_mastery.db` in the project root. Back up this file regularly.
The database is ignored by Git to help keep your study history private.

## Important limitations
- Writing scores are preliminary heuristic estimates, not official exam marks.
- This MVP does not yet call an AI API; it works without an API key.
- The question-bank table blocks exact normalized duplicates, but semantic duplicate review is not yet wired into question creation.
- Streamlit hosting storage can be ephemeral. Do not rely on a local SQLite file for permanent cloud history without configuring persistent storage or an external database.

## Next milestones
1. Add a larger curated vocabulary and grammar bank.
2. Add review queue / spaced repetition and topic filters.
3. Add optional Groq feedback with a user-supplied API key stored in Streamlit secrets.
4. Improve question similarity checks and add tests.
5. Add export/import and persistent cloud database support.
