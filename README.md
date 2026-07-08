# ConveNews

ConveNews is an application that generates personalized newsletters based on user interests by combining RSS news collection, lexical search, and Large Language Models (LLMs).

## Requirements

* Python 3.14
* It is recommended to use a virtual environment.

Install the project dependencies:

```bash
pip install -r requirements.txt
```

The text preprocessing stage also requires the following spaCy language models:

```bash
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
```

## LLM API key

The application does **not** store the LLM API key in the repository.

Instead, it expects the API key to be provided through the following environment variable:

```text
CONVENEWS_API_KEY
```

The value of this variable must be a valid API key for the LLM service configured in `config/pipeline.yaml`.

### Temporary environment variable

If you only want to use the API key during the current terminal session, you can define it temporarily.

**Windows PowerShell**

```powershell
$env:CONVENEWS_API_KEY="your_api_key"
```

**Windows CMD**

```cmd
set CONVENEWS_API_KEY=your_api_key
```

The variable will only be available during the current terminal session.

### Permanent environment variable

Alternatively, you can create a system environment variable named:

```text
CONVENEWS_API_KEY
```

and assign your API key as its value.

Using an environment variable prevents sensitive credentials from being committed to the repository or exposed in version control.

## Configuration

The application is configured through:

```text
config/pipeline.yaml
```

This file contains the configuration for the different pipeline stages, including:

* RSS crawler
* Text preprocessing
* Lexical indexer
* LLM processes

## Project structure

```text
.github/
config/
data/
src/
├── config/
├── crawler/
├── lexical_indexer/
├── llm/
├── preprocessor/
├── runners/
└── utils/
```

* `.github/` contains the project's GitHub Actions workflows.
* `config/` contains the project's configuration files.
* `data/` contains both input and output data used throughout the application.
* `src/` contains the project's source code, including:

  * `config/`, which contains the configuration loader.
  * `crawler/`, `preprocessor/`, and `lexical_indexer/`, which implement the modules that comprise the data retrieval pipeline.
  * `llm/`, which contains all LLM-related processes.
  * `runners/`, which contains the application's entry points. Production runners are located at the root of the directory, while development and testing runners are located under `dev/`.
  * `utils/`, which contains utility functions shared across multiple modules (for example, date parsing and formatting helpers).

## Running the pipeline

The pipeline is executed through the runners located in:

```text
src/runners/
```

The expected execution order is:

1. `run_crawler`
2. `run_preprocessor`
3. `run_lexical_indexer`

The repository also includes a GitHub Actions workflow that automatically executes this pipeline every day.

Development and testing runners are available under:

```text
src/runners/dev/
```

These runners are intended for testing individual modules independently during development.
