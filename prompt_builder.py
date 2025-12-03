# prompt_builder.py (IMPROVED VERSION — STRICT COLUMN FILTERING)

def build_dsl_prompt(question, schema, linking):
    used_tables = set(linking["tables"])
    used_columns = set(linking["columns"])

    # ---------------------
    # Filter schema
    # ---------------------
    relevant_schema = []
    for t in schema["tables"]:
        tname = t["table_name"]
        if tname not in used_tables:
            continue

        # keep only matched columns inside this table
        filtered_cols = [c for c in t["columns"] if c in used_columns]
        if not filtered_cols:
            continue

        relevant_schema.append({
            "table_name": tname,
            "columns": filtered_cols
        })

    # ---------------------
    # Schema DSL
    # ---------------------
    schema_dsl = ""
    for t in relevant_schema:
        schema_dsl += f"[TABLE] {t['table_name']}\n"
        for c in t["columns"]:
            schema_dsl += f"  [COLUMN] {c}\n"
        schema_dsl += "\n"

    # ---------------------
    # Linking DSL
    # ---------------------
    linking_dsl = "[LINKING]\n"
    linking_dsl += "  [MATCHED_TABLES] " + ", ".join(linking["tables"]) + "\n"
    linking_dsl += "  [MATCHED_COLUMNS] " + ", ".join(linking["columns"]) + "\n"

    linking_dsl += "  [SEMANTIC_LINKS]\n"
    for (t, c, score) in linking["semantic_pairs"]:
        if c in used_columns:  # show only selected columns
            linking_dsl += f"    - {t}.{c} (score={score:.3f})\n"

    # ---------------------
    # Final Prompt
    # ---------------------
    prompt = f"""
You are an expert Text-to-SQL generator.

You MUST use only the tables and columns listed in the [SCHEMA].
DO NOT use any column that is not included in the schema below.
Use semantic evidence from [LINKING] to resolve synonyms and ambiguity.

[SCHEMA]
{schema_dsl}

{linking_dsl}

[QUESTION]
{question}

[INSTRUCTIONS]
- Use ONLY the columns listed above.
- Prefer columns with strong semantic scores.
- Avoid adding join conditions unless they are necessary.
- Output ONLY a valid SQL query.

[SQL]
""".strip()

    return prompt
