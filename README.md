# LLM CLI

A simple, production-style **command-line interface** for chatting with **OpenAI-compatible APIs** such as [OpenRouter](https://openrouter.ai/).  
Supports model listing, single-turn and interactive chat, streaming output, and persistent conversation history.

---

## Features

- **Editable install** – live-edit code under `src/` without reinstalling.
- **Environment-based config** – secrets in `.env` (git-ignored), with `.env.example` template.
- **Multiple models** – works with any OpenAI-compatible endpoint.
- **Interactive mode** – keep a conversation alive over multiple turns.
- **Streaming output** – see tokens appear as they’re generated.
- **History store** – previous chats are saved in JSONL under `~/.llm_cli/history.jsonl`.
- **Configurable** – temperature, max tokens, system prompt, timeouts.

---

## Requirements

- Python **3.10+**
- A valid API key from your provider (e.g., [OpenRouter](https://openrouter.ai/))
- Internet connection

---

## Installation

1. **Clone this repository**

```bash
git clone https://github.com/yourname/cli-llm.git
cd cli-llm


```

2. **Create a virtual environment**

```bash
python -m venv .venv

```

3. **Activate the virtual environment**

On Windows:

```bash
.venv\Scripts\activate
```

On macOS and Linux:

```bash
source .venv/bin/activate
```

4. **Install dependencies in editable mode**

```bash
pip install -e .
```

5. **Create your .env file from .env.example:**

```bash
cp .env.example .env
```

**Edit .env and fill in:**

LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...your_key_here...
LLM_DEFAULT_MODEL=deepseek/deepseek-chat-v3-0324:free

## Usage

**List available models**

```bash
python -m llm_cli models

```

**Single-turn chat**

```bash
python -m llm_cli chat "Hello, how are you?"

```

**Interactive chat**

```bash
python -m llm_cli chat --interactive

```

Press Ctrl+C to exit.

**Specify options**

```bash
python -m llm_cli chat \
  --model deepseek/deepseek-chat-v3-0324:free \
  --temperature 0.7 \
  --max-tokens 200 \
  "Write a short poem about Kathmandu."
```

## Project Structure

```
CLI-LLM/
├── .venv/                 # Virtual environment (created locally)
├── .env                   # Local secrets/config (not in git)
├── .env.example           # Template env file
├── pyproject.toml         # Project metadata & dependencies
├── README.md              # Project documentation
└── src/
    └── llm_cli/
        ├── __init__.py    # Package marker
        ├── __main__.py    # Entry point for `python -m`
        ├── cli.py         # CLI commands (chat, models)
        ├── config.py      # Environment & chat option settings
        ├── history.py     # JSONL history persistence
        └── router.py      # HTTP client for API requests
```


## Environment Variables

| Variable            | Required | Description                                             |
| ------------------- | -------- | ------------------------------------------------------- |
| `LLM_BASE_URL`      | ✅       | Base URL for API (e.g., `https://openrouter.ai/api/v1`) |
| `LLM_API_KEY`       | ✅       | Your API key                                            |
| `LLM_DEFAULT_MODEL` | ✅       | Default model ID                                        |
| `LLM_HTTP_REFERER`  | ❌       | Optional HTTP Referer for analytics                     |
| `LLM_X_TITLE`       | ❌       | Optional app title for analytics                        |
