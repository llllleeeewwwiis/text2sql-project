# benchmark.py
import json
import sqlite3
import os
from tqdm import tqdm
from pipeline import run_text2sql, run_baseline_qwen

# -----------------------------------------------------
# CONFIG: concert_singer subset
# -----------------------------------------------------
ROOT = "spider_data/test_database/concert_singer"
DB_NAME = "concert_singer"
DB_PATH = os.path.join(ROOT, f"{DB_NAME}.sqlite")
DEV_JSON = os.path.join("spider_data/dev.json")   


# -----------------------------------------------------
# Call your Text2SQL model
# -----------------------------------------------------
def generate_sql(question, db_path):
    """
    Wrapper to your main pipeline.
    """
    # return run_text2sql(question, db_path)
    return run_baseline_qwen(question)


# -----------------------------------------------------
# Execute SQL query safely
# -----------------------------------------------------
def execute_sql(db_path, query):
    if query is None or query.strip() == "":
        return "INVALID QUERY"

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return str(e)


# -----------------------------------------------------
# Benchmark runner
# -----------------------------------------------------
def run_benchmark():
    # Load first 45 dev examples
    with open(DEV_JSON, "r", encoding="utf8") as f:
        dev_full = json.load(f)

    dev = dev_full[:45]
    print(f"Loaded {len(dev)} items for evaluation.")

    correct = 0
    total = 0

    for item in tqdm(dev):
        q = item["question"]
        gold = item["query"]

        # Run prediction
        pred = generate_sql(q, DB_PATH)

        # Execute gold & pred SQL
        gold_out = execute_sql(DB_PATH, gold)
        pred_out = execute_sql(DB_PATH, pred)

        # Compare results
        if gold_out == pred_out:
            correct += 1
        total += 1

    print("======================")
    print(f"Execution Accuracy: {correct}/{total} = {correct/total:.4f}")


if __name__ == "__main__":
    run_benchmark()
