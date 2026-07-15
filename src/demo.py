#!/usr/bin/env python3
"""Apache Ossie Demo: LLM SQL generation comparison.

Demonstrates how Apache Ossie's semantic model specification
improves LLM-generated SQL accuracy against a Postgres database.
"""

import os
import sys
from pathlib import Path
from textwrap import dedent

from dotenv import load_dotenv

from db_client import execute_query
from llm_client import generate_sql

load_dotenv(override=True)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OSSIE_MODEL_PATH = PROJECT_ROOT / "ossie" / "retail_model.yaml"

# DDL extracted from init.sql (schema only, no data)
DDL_SCHEMA = dedent("""\
    CREATE TABLE date_dim (
        d_date_sk INTEGER PRIMARY KEY,
        d_date DATE NOT NULL,
        d_year INTEGER NOT NULL,
        d_quarter_name VARCHAR(10),
        d_month_name VARCHAR(20)
    );

    CREATE TABLE customer (
        c_customer_sk INTEGER PRIMARY KEY,
        c_customer_id VARCHAR(20) NOT NULL,
        c_first_name VARCHAR(50),
        c_last_name VARCHAR(50),
        c_email_address VARCHAR(100)
    );

    CREATE TABLE item (
        i_item_sk INTEGER PRIMARY KEY,
        i_item_id VARCHAR(20) NOT NULL,
        i_item_desc VARCHAR(200),
        i_brand VARCHAR(50),
        i_category VARCHAR(50),
        i_current_price NUMERIC(7,2)
    );

    CREATE TABLE store (
        s_store_sk INTEGER PRIMARY KEY,
        s_store_id VARCHAR(20) NOT NULL,
        s_store_name VARCHAR(100),
        s_city VARCHAR(60),
        s_state VARCHAR(2),
        s_number_employees INTEGER
    );

    CREATE TABLE store_sales (
        ss_sold_date_sk INTEGER REFERENCES date_dim(d_date_sk),
        ss_item_sk INTEGER REFERENCES item(i_item_sk),
        ss_customer_sk INTEGER REFERENCES customer(c_customer_sk),
        ss_store_sk INTEGER REFERENCES store(s_store_sk),
        ss_quantity INTEGER,
        ss_sales_price NUMERIC(7,2),
        ss_ext_sales_price NUMERIC(7,2),
        ss_net_profit NUMERIC(7,2),
        ss_ticket_number INTEGER,
        PRIMARY KEY (ss_item_sk, ss_ticket_number)
    );
""")

SYSTEM_PROMPT_BASE = dedent("""\
    You are a SQL query generator for PostgreSQL.
    Given a natural language question, generate ONLY a SQL SELECT query.
    Do not include any explanation, just the SQL.
    The database has the following schema:

    {schema}
""")

SYSTEM_PROMPT_WITH_OSSIE = dedent("""\
    You are a SQL query generator for PostgreSQL.
    Given a natural language question, generate ONLY a SQL SELECT query.
    Do not include any explanation, just the SQL.
    The database has the following schema:

    {schema}

    Additionally, here is the semantic model (Apache Ossie format)
    that describes the business meaning of tables, columns,
    relationships, and pre-defined metrics:

    {ossie_model}
""")

SAMPLE_QUESTIONS = [
    "What is the total sales revenue for June?",
    "Show me sales by brand.",
    "What is the customer lifetime value?",
]


def format_results(columns, rows, max_rows=20):
    """Format query results as an aligned text table."""
    if columns is None:
        return f"  ERROR: {rows}"
    if not rows:
        return "  (no results)"

    col_widths = [len(c) for c in columns]
    for row in rows[:max_rows]:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    header = " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(columns))
    separator = "-+-".join("-" * w for w in col_widths)
    lines = [f"  {header}", f"  {separator}"]
    for row in rows[:max_rows]:
        line = " | ".join(
            str(v).ljust(col_widths[i]) for i, v in enumerate(row)
        )
        lines.append(f"  {line}")
    if len(rows) > max_rows:
        lines.append(f"  ... ({len(rows) - max_rows} more rows)")
    return "\n".join(lines)


def run_comparison(question: str, ossie_model: str):
    """Run LLM SQL generation with and without Ossie."""
    print(f"\n{'=' * 70}")
    print(f"QUESTION: {question}")
    print(f"{'=' * 70}")

    # Without Ossie
    prompt_without = SYSTEM_PROMPT_BASE.format(schema=DDL_SCHEMA)
    sql_without = generate_sql(prompt_without, question)

    print("\n--- WITHOUT Ossie (DDL only) ---")
    print(f"  SQL: {sql_without}")
    columns, rows = execute_query(sql_without)
    print("  Result:")
    print(format_results(columns, rows))

    # With Ossie
    prompt_with = SYSTEM_PROMPT_WITH_OSSIE.format(
        schema=DDL_SCHEMA, ossie_model=ossie_model
    )
    sql_with = generate_sql(prompt_with, question)

    print("\n--- WITH Ossie (DDL + Semantic Model) ---")
    print(f"  SQL: {sql_with}")
    columns, rows = execute_query(sql_with)
    print("  Result:")
    print(format_results(columns, rows))


def main():
    """Run the Apache Ossie comparison demo."""
    if not OSSIE_MODEL_PATH.exists():
        print(f"ERROR: Ossie model not found at {OSSIE_MODEL_PATH}")
        sys.exit(1)
    ossie_model = OSSIE_MODEL_PATH.read_text()

    if len(sys.argv) > 1:
        questions = [" ".join(sys.argv[1:])]
    else:
        questions = SAMPLE_QUESTIONS

    print("=" * 70)
    print("Apache Ossie Demo: LLM SQL Generation Comparison")
    print("  Database: PostgreSQL (local)")
    print(f"  Semantic Model: {OSSIE_MODEL_PATH.name}")
    provider = os.getenv("LLM_PROVIDER", "cortex")
    default_model = "llama3.1-70b" if provider == "cortex" else "llama3.1:8b"
    model = os.getenv("LLM_MODEL", default_model)
    print(f"  LLM: {provider} ({model})")
    print("=" * 70)

    for question in questions:
        run_comparison(question, ossie_model)

    print(f"\n{'=' * 70}")
    print("Demo complete.")


if __name__ == "__main__":
    main()
