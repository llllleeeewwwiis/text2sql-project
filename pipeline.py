import json
from schema_loader import load_schema_from_sqlite
from schema_linking import hybrid_linking
from prompt_builder import build_dsl_prompt
from llm_runner import OllamaRunner


def run_text2sql(question: str, db_path: str, model="qwen2.5:3b"):

    print("=== 1. Loading schema ===")
    schema = load_schema_from_sqlite(db_path)
    print("Loaded tables:", [t["table_name"] for t in schema["tables"]])

    print("\n=== 2. Running hybrid schema linking ===")
    linking = hybrid_linking(question, schema)
    print(json.dumps(linking, indent=2))

    print("\n=== 3. Building DSL Prompt ===")
    prompt = build_dsl_prompt(question, schema, linking)
    print(prompt)

    print("\n=== 4. Running LLM (Ollama) — Text2SQL Pipeline ===")
    llm = OllamaRunner(model=model, stream=False, verbose=False)
    sql = llm.run(prompt)

    print("\n=== 5. Final SQL Output (Text2SQL Pipeline) ===")
    print(sql)

    return sql


# ---------------------------------------------------------
# 🔥 Baseline：不做任何 linking、不加 DSL，直接问 Qwen
# ---------------------------------------------------------

def run_baseline_qwen(question: str, model="qwen2.5:3b"):
    """
    直接把问题丢给 Qwen 让它生成 SQL。
    """
    print("\n\n=== BASELINE: Raw Qwen Query ===")
    raw_prompt = (
        "You are a SQL expert. Convert the following natural language query into SQL.\n"
        "Return ONLY the SQL query.\n\n"
        f"Question: {question}\n\nSQL:"
    )
    print(raw_prompt)

    llm = OllamaRunner(model=model, stream=False, verbose=False)
    sql = llm.run(raw_prompt)

    print("\n=== Baseline SQL Output ===")
    print(sql)

    return sql


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":
    db = "spider_data/database/academic/academic.sqlite"
    question = "Show the title and year of all publications."

    print("\n==============================")
    print(" Running Text2SQL Pipeline ")
    print("==============================")
    pipeline_sql = run_text2sql(question, db)

    print("\n\n==============================")
    print(" Running Pure Qwen Baseline ")
    print("==============================")
    baseline_sql = run_baseline_qwen(question)
