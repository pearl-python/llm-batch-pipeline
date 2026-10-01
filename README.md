# LLM Batch Pipeline

A Python batch-processing tool that reads prompts from CSV, sends them to an LLM API, records results and errors, and saves the output to CSV.

## Features

- CSV input with pandas
- Required-column and missing-value validation
- Sequential LLM API requests
- Environment-variable configuration
- Request, HTTP, and JSON error handling
- Per-request success/failure status
- Error messages and elapsed-time recording
- CSV result export
- INFO / ERROR logging
- pytest tests with mocked API responses

## Processing Flow

```text
prompts.csv
    ↓
load_prompts()
    ↓
validate_prompts()
    ↓
send_prompt() for each row
    ↓
answer / status / error
    ↓
elapsed time
    ↓
DataFrame
    ↓
output/results.csv
    ↓
output/app.log
```

## Project Structure

```text
llm-batch-pipeline/
├─ main.py
├─ pipeline.py
├─ test_pipeline.py
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ README.md
├─ README_ja.md
├─ sample/
│  └─ prompts.csv
└─ output/
   └─ .gitkeep
```

Generated files in `output/` are ignored by Git.

## Input CSV

Example:

```csv
id,prompt
1,What is Python?
2,Explain three features of pandas.
3,Briefly explain the difference between CSV and JSON.
```

Required columns:

- `id`
- `prompt`

If a required column is missing or `prompt` contains a missing value, validation fails before API processing starts.

## Environment Variables

Copy `.env.example` to `.env`.

```env
LLM_API_URL=https://your-api.example.com/v1/chat/completions
LLM_MODEL=your-model-name
```

`.env` is excluded from Git.

The current response parser expects:

```json
{
  "choices": [
    {
      "message": {
        "content": "response text"
      }
    }
  ]
}
```

## Setup

```powershell
git clone https://github.com/pearl-python/llm-batch-pipeline.git
cd llm-batch-pipeline

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your API URL and model name.

## Run

```powershell
python main.py
```

The program writes:

- `output/results.csv`
- `output/app.log`

## Output Columns

```text
id
prompt
answer
status
error
elapsed_seconds
```

`status` is either `success` or `failed`.

On success, `error` is empty.  
On failure, `answer` is empty and the failure reason is stored in `error`.

## Logging

The application logs:

- batch start
- success/failure for each prompt
- elapsed time for each request
- error details
- total processed count
- success count
- failure count
- batch end

Example:

```text
2026-10-01 17:10:00 INFO batch start
2026-10-01 17:11:32 INFO id=1 status=success elapsed=92.15
2026-10-01 17:11:33 ERROR id=2 status=failed elapsed=0.21 error=...
2026-10-01 17:11:33 INFO batch end total=2 success=1 failed=1
```

## Tests

Run:

```powershell
python -m pytest -v
```

Current test suite: **11 tests**.

Covered cases:

- valid input
- missing required column
- missing prompt value
- result DataFrame creation
- missing API configuration
- successful API response
- HTTP error
- request exception
- JSON decode error
- CSV save
- CSV load

The API tests do not call a real LLM endpoint. They use pytest `monkeypatch` and fake responses.

pytest features used:

- `monkeypatch.setenv()`
- `monkeypatch.delenv()`
- `monkeypatch.setattr()`
- `tmp_path`

## Design Decisions

### Keep environment-dependent values outside source code
The API URL and model name are loaded from environment variables.

### Separate structured results from operational logs
`results.csv` stores batch results. `app.log` stores execution history and errors.

### Record failures per prompt
`send_prompt()` returns:

```text
answer, status, error
```

This lets the batch continue while preserving each prompt's outcome.

### Avoid live API calls in unit tests
Mocked responses make tests fast, repeatable, and independent of network/API availability.

## Current Limitations

- Sequential processing only
- No retry/backoff
- No rate-limit handling
- Response parsing assumes `choices[0].message.content`
- Input/output paths are currently fixed in the program
- Whitespace-only prompts are not separately validated
- The output directory must exist before logging starts

## Future Improvements

- retry/backoff
- rate-limit handling
- CLI arguments
- configurable paths
- whitespace-only prompt validation
- type hints
- GitHub Actions / CI
- parallel or asynchronous processing where appropriate

## Portfolio Purpose

This project demonstrates how to combine Python, pandas, an external LLM API, error handling, logging, CSV persistence, and automated tests into a small practical batch-processing workflow.
