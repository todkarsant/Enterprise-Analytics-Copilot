# Local Ollama Spider Benchmark

This is the default iterative benchmark path for Project 1.

## HARD RULE

All development, debugging, heuristic tuning, P5 characterization, and iterative benchmark runs use a local Ollama model.

**Do not use Azure OpenAI for iterative runs.** Azure is reserved for the explicitly authorized final research run after the local implementation and analysis are frozen.

## Prerequisites

- Python 3.11+
- Ollama installed and running locally
- Spider 1.0 development data available locally
- The pinned Spider evaluator checkout used by the benchmark

The benchmark does not vendor Spider data.

## Local setup

Start Ollama and pull the selected model, for example:

```bash
ollama serve
ollama pull llama3.2:1b
```

In a second shell:

```bash
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=llama3.2:1b
```

Windows PowerShell equivalent:

```powershell
$env:LLM_PROVIDER="ollama"
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
$env:OLLAMA_MODEL="llama3.2:1b"
```

## Cheap validation first

Before spending time on a benchmark:

```bash
python -m pytest -q
```

Then verify the local provider with a small smoke test or a limited benchmark.

## Limited benchmark

Use a small question count while changing prompts, heuristics, or policy logic:

```bash
python -m research.spider_benchmark \
  --questions data/spider/dev.json \
  --database-dir data/spider/database \
  --spider-eval-dir external/spider \
  --tables-file data/spider/tables.json \
  --limit 20 \
  --output artifacts/spider/p0_p5.json
```

Analyze it with:

```bash
python scripts/analyze_research_benchmark.py \
  artifacts/spider/p0_p5.json \
  --output artifacts/spider/p0_p5_analysis.json
```

## Full local characterization

Only after the limited run is stable, run the complete Spider development set and the frozen unseen-schema holdout. The GitHub Actions workflow `spider-benchmark-local` is **manual-only** and uses Ollama; it contains no Azure credentials.

The workflow accepts:

- `model`: Ollama model name; default `llama3.2:1b`
- `limit`: optional question limit; blank means the full set

## Evaluation boundary

The benchmark reports the pinned official Spider **execution evaluator** as the primary metric. This must not be described as Spider Test Suite Accuracy; Test Suite Accuracy requires the separate test-suite databases.

The row-set evaluator is retained only as a secondary diagnostic metric.

## Research sequence

```text
Code change
  -> pytest / static checks
  -> small local Ollama run
  -> local full characterization
  -> failure analysis + ablation
  -> freeze implementation
  -> final-run review
  -> explicit user authorization
  -> Azure final run
```

No push, pull request, schedule, or dependency event may trigger an Azure benchmark.
