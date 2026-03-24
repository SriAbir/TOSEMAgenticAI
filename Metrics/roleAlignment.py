import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

# =========================================================
# 1. Configuration
# =========================================================

DATA_DIR = "./conversation_excels/Test"
SUMMARY_OUTPUT_FILE = "role_alignment_summary.xlsx"

ALPHA = 0.5
K = 3.0

# =========================================================
# 2. Load embedding model
# =========================================================

model = SentenceTransformer("all-MiniLM-L6-v2")

designer_template = (
    "Provides high-level design decisions, algorithmic reasoning, requirements, pseudocode "
    "clarification, constraints, and improvement suggestions. Does not write full code."
)

programmer_template = (
    "Writes code, fixes errors, implements algorithms, responds to compiler feedback, "
    "and completes function definitions."
)

emb_designer_role = model.encode(designer_template)
emb_programmer_role = model.encode(programmer_template)

def cos_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def sigmoid(x, k=3.0):
    return 1.0 / (1.0 + np.exp(-k * x))

# =========================================================
# 3. Prepare summary output
# =========================================================

summary_rows = []

# =========================================================
# 4. Scan directory for Excel files
# =========================================================

excel_files = [
    os.path.join(DATA_DIR, f)
    for f in os.listdir(DATA_DIR)
    if f.endswith(".xlsx") and not f.startswith("~$")
]

print(f"Found {len(excel_files)} Excel files in {DATA_DIR}")

# =========================================================
# 5. Process each Excel file
# =========================================================

for file_path in excel_files:
    print(f"\nProcessing: {file_path}")

    df = pd.read_excel(file_path)

    # KEEP empty rows to preserve parity
    utterances = df.iloc[:, 1].astype(str).tolist()

    role_alignment_scores = []
    role_labels = []

    # -----------------------------------------------------
    # Compute RA score per turn
    # -----------------------------------------------------

    for i, utt in enumerate(utterances):

        # EVEN rows = Programmer, ODD rows = Designer
        expected_role = "Programmer" if i % 2 == 0 else "Designer"

        # Empty row → neutral
        if utt is None or not utt.strip():
            RA = 0.0
            role = "Empty"

        else:
            emb = model.encode(utt)
            simP = cos_sim(emb, emb_programmer_role)
            simD = cos_sim(emb, emb_designer_role)

            if expected_role == "Programmer":
                RA = simD - simP
                role = "Programmer"
            else:
                RA = simP - simD
                role = "Designer"

        role_alignment_scores.append(RA)
        role_labels.append(role)

    RA_scores = np.array(role_alignment_scores)
    N = len(RA_scores)

    # -----------------------------------------------------
    # Aggregate metrics
    # -----------------------------------------------------

    A = np.sum(RA_scores > 0) / N                # % aligned turns
    M = np.mean(RA_scores)                       # mean RA
    sigma_M = sigmoid(M, K)                      # sigmoid-normalized mean
    RAI = ALPHA * A + (1 - ALPHA) * sigma_M      # final score

    summary_rows.append({
        "File": os.path.basename(file_path),
        "Turns": N,
        "Mean_RA": M,
        "Min_RA": np.min(RA_scores),
        "Percent_Aligned": A,
        "Sigmoid_Mean_RA": sigma_M,
        "Final_RAI": RAI
    })

    # -----------------------------------------------------
    # Save per-utterance detailed output
    # -----------------------------------------------------

    out_df = pd.DataFrame({
        "Utterance": utterances,
        "Role": role_labels,
        "RA_Score": RA_scores
    })

    out_filename = os.path.join(
        DATA_DIR,
        os.path.basename(file_path).replace(".xlsx", "_role_alignment_output.xlsx")
    )

    out_df.to_excel(out_filename, index=False)
    print(f"Saved detailed results: {out_filename}")

# =========================================================
# 6. Save consolidated summary Excel
# =========================================================

summary_df = pd.DataFrame(summary_rows)
summary_df.to_excel(SUMMARY_OUTPUT_FILE, index=False)

print("\nAll done!")
print(f"Saved consolidated summary to: {SUMMARY_OUTPUT_FILE}")
