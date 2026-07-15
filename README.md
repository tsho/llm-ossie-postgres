# LLM + Apache Ossie + Postgres Demo

## Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Python | >= 3.11 | Managed with [uv](https://docs.astral.sh/uv/) |
| PostgreSQL | 18+ (latest) | Docker (`postgres:latest`) or local install |
| Docker | 24+ | Docker Compose V2 included |
| LLM | Any chat completion API | This demo uses Snowflake Cortex (`llama3.1-70b`) by default; also supports local [Ollama](https://ollama.com/). Any OpenAI-compatible API can be added. |

---

This demo shows how **Apache Ossie** (semantic model metadata) improves LLM-generated SQL accuracy when querying a PostgreSQL database.

## What This Demonstrates

The same natural language question is sent to an LLM twice:
1. **Without Ossie** — only the raw DDL schema is provided
2. **With Ossie** — DDL + Apache Ossie semantic model (YAML) is provided

The generated SQL is executed against Postgres, and results are compared side-by-side.

### Why Results Differ

| Scenario | Without Ossie | With Ossie |
|----------|--------------|------------|
| "Total sales for June?" | May use `SUM(ss_sales_price)` (unit price) | Uses `SUM(ss_ext_sales_price)` (correct: qty * price) |
| "Sales by brand?" | May miss JOIN to `item` table | Uses defined relationship `ss_item_sk → i_item_sk` |
| "Customer LTV?" | Returns total sales (not per-customer) | Uses pre-defined metric: `SUM / COUNT(DISTINCT customer)` |

## Setup

```bash
# 1. Start Postgres (Docker)
docker compose up -d

# Or use local Postgres:
# createdb demo && psql -d demo -f db/init.sql

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set LLM_PROVIDER and Postgres connection

# 4. Run the demo
python src/demo.py
```

## LLM Providers

### Snowflake Cortex (default)

Uses your `~/.snowflake/connections.toml` PAT token automatically.

```bash
# .env
LLM_PROVIDER=cortex
LLM_MODEL=llama3.1-70b  # or: mistral-large2, llama3.1-8b
```

### Local LLM (Ollama)

```bash
# Install and start Ollama: https://ollama.com/
ollama pull llama3.1:8b

# .env
LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
OLLAMA_BASE_URL=http://localhost:11434
```

## Custom Questions

```bash
python src/demo.py "What are the top 3 stores by revenue?"
```

## Project Structure

```
├── docker-compose.yml          # Postgres (latest) container
├── db/
│   └── init.sql                # TPC-DS subset DDL + seed data
├── ossie/
│   └── retail_model.yaml       # Apache Ossie semantic model
├── src/
│   ├── demo.py                 # Main comparison script
│   ├── llm_client.py           # LLM provider abstraction (Cortex / Ollama)
│   └── db_client.py            # Postgres connection
├── requirements.txt
├── .env.example
└── README.md
```

## Apache Ossie

[Apache Ossie](https://github.com/apache/ossie) (incubating, formerly OSI - Open Semantic Interchange) is a vendor-agnostic semantic model specification. It provides:

- **`ai_context`** — Instructions and synonyms that help LLMs understand business meaning
- **`metrics`** — Pre-defined calculations (e.g., revenue = `SUM(ss_ext_sales_price)`)
- **`relationships`** — JOIN conditions between datasets
- **`fields`** — Column-level descriptions clarifying ambiguous names

## TODO

- [ ] Add alternative dataset: simple e-commerce model (orders, products, users) for a more intuitive demo
- [ ] Add Snowflake Postgres support as a backend option (replace local Docker with Snowflake-managed Postgres)
- [ ] Add automated evaluation (compare expected vs actual SQL output)
- [ ] Add interactive mode (REPL for ad-hoc questions)
- [ ] Visualize results in a Streamlit app

## License

Apache License 2.0
