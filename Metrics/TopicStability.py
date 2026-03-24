import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer, util


# ============================================================
# 1. CODE → NATURAL LANGUAGE SUMMARY
# ============================================================
def summarize_code(code: str) -> str:
    code_lower = code.lower()
    summary_parts = []

    if "fib" in code_lower or "fibonacci" in code_lower:
        summary_parts.append("This turn discusses Fibonacci logic or Fibonacci quiz functionality.")

    if "play_game" in code_lower or "quiz" in code_lower or "score" in code_lower:
        summary_parts.append("It describes gameplay mechanics, scoring, or question generation.")

    if "difficulty" in code_lower:
        summary_parts.append("It includes difficulty level settings or adaptive question ranges.")

    if "scanf" in code_lower or "fgets" in code_lower:
        summary_parts.append("It handles user input validation and buffer clearing.")

    if "ullong" in code_lower or "overflow" in code_lower:
        summary_parts.append("It discusses overflow protection for Fibonacci calculations.")

    if not summary_parts:
        summary_parts.append("General C program logic related to computation or quizzes.")

    return " ".join(summary_parts)


# ============================================================
# 2. KEYWORD EXTRACTION (BOOSTER)
# ============================================================
def extract_keywords(text: str) -> str:
    text = text.lower()
    keywords = set()

    if "fibonacci" in text or "fib" in text:
        keywords |= {"fibonacci", "fibonacci-sequence", "fib-number", 
                     "fib-game", "sequence-position", "math-sequence"}

    if "game" in text or "quiz" in text or "rounds" in text:
        keywords |= {"gameplay", "quiz-mechanics", "rounds", "scoring",
                     "question-generation", "user-interaction"}

    if "difficulty" in text:
        keywords |= {"difficulty-levels", "adaptive-gameplay"}

    if "scanf" in text or "fgets" in text:
        keywords |= {"input-validation", "buffer-management"}

    if "overflow" in text or "ullong" in text:
        keywords |= {"overflow-protection", "safe-arithmetic"}

    if "rand" in text:
        keywords |= {"randomized-questions", "random-selection"}

    # Always anchor domain knowledge
    keywords |= {"c-program", "code-review", "program-logic"}

    boosted = " ".join(keywords) + " " + " ".join(keywords)
    return boosted


# ============================================================
# 3. TASK PROTOTYPE (GLOBAL TOPIC VECTOR)
# ============================================================
TASK_PROTOTYPE = """
This task involves writing and improving a mathematical Fibonacci game in C.
It should involve Fibonacci number calculation and a gameplay loop, including
rounds, scoring, user interaction, and quiz mechanics.
"""

# ============================================================
# 4. BUILD EMBEDDING TEXT
# ============================================================
def build_embedding_text(turn: str) -> str:
    summary = summarize_code(turn)
    keywords = extract_keywords(turn)
    clean_turn = turn[:1500]  # ensure no overly long embedding input

    final_text = (
        f"SUMMARY: {summary}\n"
        f"KEYWORDS: {keywords}\n"
        f"CONTENT: {clean_turn}"
    )
    return final_text


# ============================================================
# 5. MAIN TOPIC SIMILARITY FUNCTION (FILE-BASED)
# ============================================================
def compute_topic_similarity_from_file(filepath: str, content_column="content"):

    model = SentenceTransformer("all-MiniLM-L6-v2")
    task_emb = model.encode(TASK_PROTOTYPE, convert_to_tensor=True)

    df = pd.read_excel(filepath)
    turns = df[content_column].dropna().tolist()

    similarities = []

    for turn in turns:
        emb_text = build_embedding_text(turn)
        turn_emb = model.encode(emb_text, convert_to_tensor=True)
        sim = util.cos_sim(turn_emb, task_emb).item()
        similarities.append(sim)

    return similarities


# ============================================================
# 6. PLOT + FINAL SCORE
# ============================================================
def plot_topic_similarity(similarities, output="topic_similarity.png"):
    plt.figure(figsize=(10, 4))
    plt.plot(similarities, marker='o')
    plt.title("Topic Similarity Over Turns")
    plt.xlabel("Turn Number")
    plt.ylabel("Similarity to Task Prototype")
    plt.ylim(0, 1)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output)
    plt.close()
    print(f"Saved plot to {output}")


def compute_final_stability(similarities, last_k=3):
    if len(similarities) < last_k:
        return np.mean(similarities)
    return float(np.mean(similarities[-last_k:]))


# ============================================================
# 7. RUN EVERYTHING
# ============================================================
if __name__ == "__main__":
    filepath = "conversation.xlsx"  # CHANGE THIS

    similarities = compute_topic_similarity_from_file(filepath)

    print("\n=== PER-TURN TOPIC SIMILARITY ===")
    for i, s in enumerate(similarities):
        print(f"Turn {i+1}: {s:.4f}")

    final_score = compute_final_stability(similarities)
    print("\n=== FINAL TOPIC STABILITY SCORE ===")
    print(round(final_score, 4))

    plot_topic_similarity(similarities)
