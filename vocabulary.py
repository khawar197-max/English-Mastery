import json
import random
from pathlib import Path

def load_words():
    path = Path(__file__).resolve().parents[1] / "data" / "vocabulary.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)

def make_vocab_question(words):
    item = random.choice(words)
    distractors = [w["meaning"] for w in words if w["meaning"] != item["meaning"]]
    options = random.sample(distractors, min(3, len(distractors))) + [item["meaning"]]
    random.shuffle(options)
    return {
        "word": item["word"],
        "prompt": "Choose the closest meaning.",
        "options": options,
        "answer": item["meaning"],
        "explanation": item.get("example", "")
    }
