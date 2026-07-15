"""LLM client for Snowflake Cortex and local Ollama."""

import os
import tomllib
from pathlib import Path

import requests


def _load_snowflake_connection():
    """Load Snowflake connection from ~/.snowflake/connections.toml."""
    toml_path = Path.home() / ".snowflake" / "connections.toml"
    if not toml_path.exists():
        raise FileNotFoundError(f"connections.toml not found at {toml_path}")

    with open(toml_path, "rb") as f:
        config = tomllib.load(f)

    conn_name = os.getenv(
        "SNOWFLAKE_CONNECTION_NAME",
        config.get("default_connection_name", ""),
    )
    if not conn_name:
        raise ValueError(
            "No SNOWFLAKE_CONNECTION_NAME set and no "
            "default_connection_name in toml"
        )

    conn = config.get(conn_name)
    if not conn:
        raise ValueError(
            f"Connection '{conn_name}' not found in connections.toml"
        )

    return conn


def _generate_sql_cortex(system_prompt: str, question: str) -> str:
    """Generate SQL using Snowflake Cortex AI Complete API."""
    conn = _load_snowflake_connection()
    account = conn["account"]
    token = conn.get("token", os.getenv("SNOWFLAKE_TOKEN", ""))

    if not token:
        raise ValueError(
            "No PAT token found in connection config or SNOWFLAKE_TOKEN env var"
        )

    model = os.getenv("LLM_MODEL", "llama3.1-70b")
    url = (
        f"https://{account}.snowflakecomputing.com"
        "/api/v2/cortex/inference:complete"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Snowflake-Authorization-Token-Type": ("PROGRAMMATIC_ACCESS_TOKEN"),
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "temperature": 0,
        "max_tokens": 2048,
        "stream": False,
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def _generate_sql_ollama(system_prompt: str, question: str) -> str:
    """Generate SQL using local Ollama (OpenAI-compatible API)."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("LLM_MODEL", "llama3.1:8b")
    url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        "temperature": 0,
        "max_tokens": 2048,
        "stream": False,
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()


def generate_sql(system_prompt: str, question: str) -> str:
    """Generate SQL using configured LLM provider."""
    provider = os.getenv("LLM_PROVIDER", "cortex")

    if provider == "cortex":
        content = _generate_sql_cortex(system_prompt, question)
    elif provider == "ollama":
        content = _generate_sql_ollama(system_prompt, question)
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. Use 'cortex' or 'ollama'."
        )

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.split("\n")
        lines = [line for line in lines if not line.startswith("```")]
        content = "\n".join(lines).strip()

    return content
