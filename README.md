# aiagent

A small command-line AI coding agent. It asks an LLM (via OpenRouter) what to do, runs the
tool it requests — list files, read a file, write a file, execute Python — feeds the result
back, and loops until the model answers in plain text.

## Features

- Bounded tool-calling loop (`MAX_ITERATIONS = 20`)
- Four tools: `get_files_info`, `get_file_content`, `write_file`, `run_python_file`
- All tool paths resolve inside a single working directory (`./calculator`)
- `--verbose` prints prompt/completion token usage per request
- Pure core + explicit effect boundaries in `main.py`; the tool executor is injectable

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)
- An [OpenRouter](https://openrouter.ai/) API key

## Setup

```bash
git clone <your-repo-url> && cd aiagent
uv sync
cp .env.example .env      # then put your real key in .env
```

`.env` is git-ignored. Never commit it.

## Usage

```bash
uv run main.py "list the files in the calculator directory"
uv run main.py "add a docstring to calculator/pkg/calculator.py" --verbose
```

## Project layout

```text
main.py              CLI, pure core, composition root
prompts.py           system prompt
config.py            working directory + max characters per file read
functions/           tool implementations and their JSON schemas
calculator/          sample project the agent operates on
test_*.py            manual smoke scripts, one per tool
calculator/tests.py  unittest suite for the sample calculator
```

## Tests

```bash
uv run python calculator/tests.py        # unittest suite (exit code is the gate)
uv run python test_get_files_info.py     # smoke scripts print, they do not assert
```

## Notes

- The agent executes Python with your user privileges and can overwrite files under
  `calculator/`. Run it on a checkout you can afford to lose.
- `pyrightconfig.json` sets `extraPaths` to `"."`, so type-checking works from any clone path.
