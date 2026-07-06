import sys
import os

# Add judge folder to path
JUDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "judge")
sys.path.append(JUDGE_DIR)

import joblib
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

class JudgmentService:
    def __init__(self):
        # Store original directory
        original_dir = os.getcwd()
        
        # Load files from judge directory
        os.chdir(JUDGE_DIR)
        self.retrieval_vectorizer = joblib.load("retrieval_vectorizer.pkl")
        self.tfidf_matrix = load_npz("retrieval_tfidf_matrix.npz")
        self.df_labeled_full = pd.read_csv("judgments_final.csv")
        self.df_labeled_full = self.df_labeled_full[self.df_labeled_full["outcome"] != "Unknown"].reset_index(drop=True)
        
        # Restore original directory
        os.chdir(original_dir)
        
        print(f"✅ Judgment Service Ready! {self.tfidf_matrix.shape[0]} cases indexed.")

    def get_key_sections(self, text, total_words=2000):
        words = str(text).split()
        n = len(words)
        head = words[:500]
        tail = words[max(0, n-1500):]
        return " ".join(head + tail)

    def get_case_summary(self, text):
        words = str(text).split()
        n = len(words)
        head = " ".join(words[:100])
        middle = " ".join(words[n//2 - 50 : n//2 + 50])
        tail = " ".join(words[max(0, n-100):])
        return {"background": head, "arguments": middle, "judgment": tail}

    def find_similar_cases(self, query_text, top_n=5):
        query_vec = self.retrieval_vectorizer.transform([self.get_key_sections(query_text)])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_n]
        
        results = []
        for rank, idx in enumerate(top_indices, 1):
            row = self.df_labeled_full.iloc[idx]
            citation = str(row["citation"]) if str(row["citation"]) != "nan" else "N/A"
            summary = self.get_case_summary(str(row["clean_text"]))
            
            results.append({
                "rank": rank,
                "similarity": round(float(similarities[idx]) * 100, 1),
                "case_title": row["case_title"],
                "year": int(row["year"]),
                "petitioner": row["petitioner"],
                "respondent": row["respondent"],
                "outcome": row["outcome"],
                "citation": citation,
                "background": summary["background"],
                "arguments": summary["arguments"],
                "judgment": summary["judgment"],
                "word_count": int(row["word_count_clean"]),
                "page_count": int(row["page_count"])
            })
        
        return results
