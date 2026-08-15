# Troubleshooting

## Ollama: `bind: Only one usage of each socket address`

Ollama is already listening on port 11434. Do not start a second server.

Verify:

```bat
curl http://127.0.0.1:11434/api/version
curl http://127.0.0.1:11434/api/tags
```

## Run project commands from repository root

```bat
cd D:\Private\Git_Portfolio
python -m scripts.init_db
pytest -q
uvicorn app.main:app --reload
```

## LLM summarization JSON errors

V0.2.1 tolerates fenced/extra JSON from Ollama and falls back to deterministic result summaries if the LLM response cannot be parsed.

## Relative dates

The demo uses dataset-relative time for phrases such as "last month". This avoids comparing the question to the user's wall-clock month when the sample dataset is historical.


## Pytest returns 422 for `test_query_mock`

If your `.env` uses `LLM_PROVIDER=ollama`, the API test must not depend on that
local runtime configuration. V0.2.2 forces the Mock provider during tests.

Use:

```bash
python -m pytest -q
```

The application itself may continue using Ollama in `.env`.
