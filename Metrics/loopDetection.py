import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import matplotlib.pyplot as plt

# ---------------------------- CONFIG ----------------------------
INPUT_FOLDER = "./conversation/Test"   # Change to your folder
SUMMARY_OUTPUT_FILE = "loop_detection_summary.xlsx"
WINDOW_SIZE = 10
LOOP_THRESHOLD = 1
MODEL_NAME = "all-MiniLM-L6-v2"

# ----------------------- LOAD MODEL -----------------------------
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# --------------------- CORE LOOP DETECTION ----------------------
def compute_loop_scores(turn_texts, window_size=WINDOW_SIZE):
    embeddings = model.encode(turn_texts, convert_to_tensor=True)
    loop_scores = []

    for t in range(len(turn_texts)):
        if t == 0:
            loop_scores.append(0.0)
            continue
        start = max(0, t - window_size)
        context_embeds = embeddings[start:t]
        sims = util.cos_sim(embeddings[t], context_embeds)
        max_sim = float(sims.max())
        loop_scores.append(max_sim)

    return loop_scores

# ------------------------ PLOTTING ------------------------------
def plot_loop_scores(loop_scores, save_path):
    plt.figure(figsize=(12, 5))
    plt.plot(loop_scores, marker='o', color='orange', label="Loop Score")
    plt.axhline(LOOP_THRESHOLD, color='red', linestyle='--', label="Loop Threshold (0.85)")
    plt.title("Loop Detection Metric Across Conversation Turns")
    plt.xlabel("Turn Number")
    plt.ylabel("Loop Score (0–1)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Plot saved: {save_path}")

# --------------------------- MAIN -------------------------------
summary_rows = []

excel_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".xlsx") and not f.startswith("~$")]

print(f"Found {len(excel_files)} Excel files in {INPUT_FOLDER}.")

for file in excel_files:
    file_path = os.path.join(INPUT_FOLDER, file)
    print(f"\nProcessing: {file}")

    df = pd.read_excel(file_path)

    if "content" not in df.columns:
        print(f"Skipped {file} — missing 'content' column.")
        continue

    if "turn_number" not in df.columns:
        df["turn_number"] = np.arange(1, len(df) + 1)

    turn_texts = df["content"].fillna("").astype(str).tolist()
    loop_scores = compute_loop_scores(turn_texts)

    df["LoopScore"] = loop_scores

    # Save detailed output
    output_file = os.path.join(INPUT_FOLDER, file.replace(".xlsx", "_loop_output.xlsx"))
    df.to_excel(output_file, index=False)

    # Save plot
    plot_path = os.path.join(INPUT_FOLDER, file.replace(".xlsx", "_loop_plot.png"))
    plot_loop_scores(loop_scores, plot_path)

    # Aggregate Loop Detection Score (mean of scores > threshold)
    strong_loops = [score for score in loop_scores if score >= LOOP_THRESHOLD]
    mean_loop_score = np.mean(strong_loops) if strong_loops else 0.0

    summary_rows.append({
        "File": file,
        "Turns": len(turn_texts),
        "Mean_LoopScore": np.mean(loop_scores),
        "StrongLoopCount": len(strong_loops),
        "LoopScore_GT_Threshold_Mean": mean_loop_score,
        "Repetition Ratio": mean_loop_score/len(turn_texts)
    })

# Save summary
summary_df = pd.DataFrame(summary_rows)
summary_df.to_excel(SUMMARY_OUTPUT_FILE, index=False)
print(f"\nSaved final summary to: {SUMMARY_OUTPUT_FILE}")
