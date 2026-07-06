
import joblib
import pandas as pd
import numpy as np
import re
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

# ── LOAD ALL SAVED FILES ──────────────────────────────────
baseline_model       = joblib.load("outcome_predictor.pkl")
retrieval_vectorizer = joblib.load("retrieval_vectorizer.pkl")
tfidf_matrix         = load_npz("retrieval_tfidf_matrix.npz")
df_index             = pd.read_csv("case_index.csv")
df_labeled_full      = pd.read_csv("judgments_final.csv")
df_labeled_full      = df_labeled_full[df_labeled_full["outcome"] != "Unknown"].reset_index(drop=True)
print(f"✅ Ready! {tfidf_matrix.shape[0]} cases indexed.")


def get_key_sections(text, total_words=2000):
    words = str(text).split()
    n = len(words)
    head = words[:500]
    tail = words[max(0, n-1500):]
    return " ".join(head + tail)


def get_case_summary(text):
    words = str(text).split()
    n = len(words)
    head   = " ".join(words[:100])
    middle = " ".join(words[n//2 - 50 : n//2 + 50])
    tail   = " ".join(words[max(0, n-100):])
    return {"background": head, "arguments": middle, "judgment": tail}


def find_similar_cases(query_text, top_n=5):
    query_vec    = retrieval_vectorizer.transform([get_key_sections(query_text)])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices  = similarities.argsort()[::-1][:top_n]
    results = []
    for rank, idx in enumerate(top_indices, 1):
        row      = df_labeled_full.iloc[idx]
        citation = str(row["citation"]) if str(row["citation"]) != "nan" else "N/A"
        summary  = get_case_summary(str(row["clean_text"]))
        results.append({
            "rank"       : rank,
            "similarity" : round(float(similarities[idx]) * 100, 1),
            "case_title" : row["case_title"],
            "year"       : row["year"],
            "petitioner" : row["petitioner"],
            "respondent" : row["respondent"],
            "outcome"    : row["outcome"],
            "citation"   : citation,
            "filename"   : row["filename"],
            "background" : summary["background"],
            "arguments"  : summary["arguments"],
            "judgment"   : summary["judgment"],
            "word_count" : row["word_count_clean"],
            "page_count" : row["page_count"]
        })
    return results


def analyze_case(text, top_n=5):
    processed     = get_key_sections(text)
    prediction    = baseline_model.predict([processed])[0]
    probabilities = baseline_model.predict_proba([processed])[0]
    classes       = baseline_model.classes_
    prob_dict     = dict(zip(classes, probabilities))
    prob_sorted   = dict(sorted(prob_dict.items(), key=lambda x: x[1], reverse=True))
    similar_cases = find_similar_cases(text, top_n=top_n)

    outcome_counts = {}
    for c in similar_cases:
        outcome_counts[c["outcome"]] = outcome_counts.get(c["outcome"], 0) + 1
    dominant = max(outcome_counts, key=outcome_counts.get)

    print("=" * 65)
    print("   ⚖️  AI LEGAL CASE ANALYSIS REPORT")
    print("=" * 65)
    print(f"\n   🔮 PREDICTED OUTCOME  :  {prediction}")
    print(f"\n   📊 CONFIDENCE SCORES  :")
    for outcome, prob in prob_sorted.items():
        bar    = "█" * int(prob * 30)
        marker = " ← predicted" if outcome == prediction else ""
        print(f"      {outcome:<16} {prob*100:5.1f}%  {bar}{marker}")

    print(f"\n   📈 PRECEDENT ANALYSIS :")
    print(f"      Among top {top_n} similar cases:")
    for outcome, count in sorted(outcome_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"      {outcome:<16} {count} cases  {'█' * count}")
    print(f"      Precedent trend  → {dominant}")

    print(f"\n   📚 TOP {top_n} SIMILAR PAST CASES")
    print("   " + "=" * 62)
    for case in similar_cases:
        print(f"\n   ┌─ #{case['rank']}  [{case['similarity']}% similarity]  Outcome: {case['outcome']}")
        print(f"   │  📌 Title      : {case['case_title'][:60]}")
        print(f"   │  📅 Year       : {case['year']}  | Pages: {case['page_count']}  | Words: {case['word_count']}")
        print(f"   │  👤 Petitioner : {case['petitioner'][:55]}")
        print(f"   │  👤 Respondent : {case['respondent'][:55]}")
        print(f"   │  📖 Citation   : {case['citation'][:60]}")
        print(f"   │")
        print(f"   │  📋 BACKGROUND :\n   │     {case['background']}")
        print(f"   │")
        print(f"   │  ⚔️  ARGUMENTS  :\n   │     {case['arguments']}")
        print(f"   │")
        print(f"   │  ⚖️  JUDGMENT   :\n   │     {case['judgment']}")
        print(f"   └─" + "─" * 62)

    return prediction, prob_sorted, similar_cases
