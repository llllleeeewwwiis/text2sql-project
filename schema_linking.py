# schema_linking.py (IMPROVED — STRICT SCORE THRESHOLD + BETTER MERGE)

import re
from difflib import SequenceMatcher
import numpy as np
from sentence_transformers import SentenceTransformer

_embedder = SentenceTransformer("all-MiniLM-L6-v2")

GENERIC_PRIOR = {
    "name": 0.25,
    "id": 0.30,
    "homepage": 0.20,
    "year": 0.05,
    "title": 0.05,
}

def get_penalty(col):
    return GENERIC_PRIOR.get(col.lower(), 0.0)

def extract_foreign_keys(schema):
    fk = {}
    for t in schema["tables"]:
        tname = t["table_name"]
        for c in t["columns"]:
            if c.lower().endswith("id"):
                fk.setdefault(c, []).append(tname)
    return fk


# --------------------------------------------------
# Lexical Linking (strict version)
# --------------------------------------------------
def lexical_linking(question, schema):
    q = question.lower()
    matched_tables = set()
    col_scores = {}

    for t in schema["tables"]:
        tname = t["table_name"].lower()
        if tname in q:
            matched_tables.add(t["table_name"])

        for c in t["columns"]:
            cname = c.lower()

            score = 0.0
            if cname in q:
                score = 1.0
            else:
                ratio = SequenceMatcher(None, cname, q).ratio()
                if ratio > 0.80:  # stricter
                    score = ratio

            if score > 0:
                score -= get_penalty(c)
                if score > 0:
                    col_scores[c] = score

    return matched_tables, col_scores


# --------------------------------------------------
# Semantic Linking (threshold raised)
# --------------------------------------------------
def semantic_linking(question, schema):
    question_emb = _embedder.encode([question])[0]

    col_items = []
    for t in schema["tables"]:
        for c in t["columns"]:
            col_items.append((t["table_name"], c))

    texts = [f"{t} {c}" for (t, c) in col_items]
    embs = _embedder.encode(texts)

    sims = np.dot(embs, question_emb) / (
        np.linalg.norm(embs, axis=1) * np.linalg.norm(question_emb)
    )

    results = []
    for (t, c), sim in zip(col_items, sims):
        score = sim - get_penalty(c)
        if score >= 0.55:   # ← main fix
            results.append((t, c, score))

    return results


# --------------------------------------------------
# Hybrid Linking (filtered merge)
# --------------------------------------------------
def hybrid_linking(question, schema):
    lex_tables, lex_cols = lexical_linking(question, schema)
    sem_pairs = semantic_linking(question, schema)

    # merge scores
    col_scores = dict(lex_cols)
    for (t, c, s) in sem_pairs:
        col_scores[c] = max(col_scores.get(c, 0), s)

    # final columns after filtering
    final_cols = [c for c, s in col_scores.items() if s > 0]

    # table selection: only keep tables containing matched columns
    tables_with_cols = set()
    for t in schema["tables"]:
        tname = t["table_name"]
        table_cols = set(t["columns"])
        if table_cols & set(final_cols):
            tables_with_cols.add(tname)

    # merge lexical table matches
    final_tables = tables_with_cols | lex_tables

    # return values
    used_sem_pairs = [(t, c, s) for (t, c, s) in sem_pairs if c in final_cols]

    return {
        "tables": list(final_tables),
        "columns": final_cols,
        "semantic_pairs": used_sem_pairs,
    }
