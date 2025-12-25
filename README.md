## NLQ_TO_SQL_CHATBOT

NLQ_TO_SQL_CHATBOT is a lightweight Python project that converts Natural Language Queries (NLQ) into safe SQL queries, executes them against a local SQLite analytics database, and returns concise, business-friendly answers. The project is built with LangGraph, LangChain, and OpenAI-compatible LLMs and includes utilities to prepare local CSV data, create indexes, and trace executions via Langsmith/MLflow.

Key goals:
- Turn user questions about the student domain into validated SELECT SQL queries.
- Execute only safe SELECT queries against a local SQLite DB.
- Return concise plain-text answers to users while preserving full execution traces for observability.

This repository is designed as a template / learning playground for building NLQ→SQL agents.

---

## Features

- Intent detection for student-domain queries (students, courses).
- Structured SQL generation with schema context and confidence score.
- Safe SQL execution (SELECT-only) using a dedicated `execute_sql` tool.
- Clear separation of nodes: intent check → SQL generation → SQL execution → answer formatting.
- Console runner with a `verbose` mode for debugging and a non-verbose default for clean user output.
- Tests for data loader utilities.
- LangGraph + Langsmith tracing for per-node observability.

---

## Repository Layout

- `main.py` — Console runner that compiles the workflow and streams the final answer. Defaults to non-verbose output.
- `src/Agent/` — Core agent implementation
	- `nodes.py` — Workflow nodes (intent check, SQL generation, SQL execution wrapper, answer formatting).
	- `tools.py` — Tool implementations (e.g., `execute_sql`).
	- `workflow.py` — Assembles the StateGraph (node registration and edges).
	- `routers.py` — Branching logic between nodes.
	- `Grapgh_state.py` — Agent state TypedDict definitions.
- `scripts/Load_Data.py` — Utilities to load CSV files into a local SQLite DB and create indexes.
- `data/` — Example `csv/` and `sqlite/` folders (holds sample CSVs and DB config).
- `tests/` — Pytest tests (e.g., `test_dataloader.py`).
- `Notebooks/` — Example notebook templates and experiments.

---

## Quick Start

Prerequisites

- Python 3.10+ (recommended)
- An OpenAI-compatible LLM key (set `OPENAI_API_KEY` in your environment or `.env`).

Install dependencies

```powershell
pip install -r requirements.txt
```

Load example CSV data into the local SQLite DB (from repo root):

```powershell
python -c "from scripts.Load_Data import DataLoader; loader=DataLoader(); print(loader.load_data('data/csv'))"
```

Run the chat runner (non-verbose, prints only final answer):

```powershell
python main.py
```

Example queries:

- `how many students are there in total`
- `show me department wise students enrolled`
- `what is the average GPA by city?`

To enable verbose output (show intermediate messages for debugging), edit the `run_main` call in `main.py` to pass `verbose=True` or modify the `__main__` block to set verbose.

---

## How it works (high-level)

1. The console runner (`main.py`) loads the StateGraph from `src/Agent/workflow.py` and compiles it.
2. User input is seeded into the initial state as a `HumanMessage`.
3. `check_intent` node uses a structured LLM call (via `with_structured_output`) to determine whether the question is relevant and which tables to use.
4. `generate_sql` node produces a high-confidence, SELECT-only SQL query (returned in `generated_sql`). An internal AIMessage containing the SQL is attached so the execution step can pick it up.
5. `execute_sql_node` (wrapper) executes the SQL via `execute_sql` (a safe SELECT-only tool) and sets `query_result` in the agent state.
6. `format_final_answer` summarizes `query_result` into a concise plain-text answer for the user.

---

## Developer notes & troubleshooting

- If you see `sqlite3.OperationalError: unable to open database file`, ensure the DB parent directories exist and are writable. The loader now creates parent directories automatically, or use an absolute path for `DataLoader`.
- If the LLM fails to call tools (ValueError about unsupported function), we avoid `bind_tools` with raw tool objects — instead the workflow uses an explicit wrapper node to call `execute_sql` directly.
- To debug intermediate steps, set `verbose=True` in `run_main(...)` or enable Langsmith tracing (set `LANGSMITH_TRACING=true` and provide `LANGSMITH_API_KEY`). Traces will include node inputs/outputs and make it easy to inspect `generated_sql`, `query_result`, and intent metadata.

---



## Next improvements (ideas)

- Add a CI workflow to run tests and linting on push.
- Add more robust schema introspection and multi-table join handling.
- Support optional function-calling integration with OpenAI by converting tools to JSON-schema/pydantic function models.
- Add more unit tests around edge cases (empty tables, permission errors, malicious inputs).

---




