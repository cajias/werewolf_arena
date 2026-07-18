```text
__        __                              _  __    _
\ \      / /__ _ __ _____      _____  | |/ _|  / \   _ __ ___ _ __   __ _
 \ \ /\ / / _ \ '__/ _ \ \ /\ / / _ \ | | |_  / _ \ | '__/ _ \ '_ \ / _` |
  \ V  V /  __/ | |  __/\ V  V / (_) || |  _|/ ___ \| | |  __/ | | | (_| |
   \_/\_/ \___|_|  \___| \_/\_/ \___/ |_|_| /_/   \_\_|  \___|_| |_|\__,_|
```

<p align="center">
  <strong>Pit LLMs against each other in Werewolf and measure who can lie, reason, and survive.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/cajias/werewolf_arena"></a>
  <img alt="Top language" src="https://img.shields.io/github/languages/top/cajias/werewolf_arena">
  <img alt="Last commit" src="https://img.shields.io/github/last-commit/cajias/werewolf_arena">
  <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/cajias/werewolf_arena/ci.yml?branch=main&label=CI">
  <img alt="Python" src="https://img.shields.io/badge/python-3.8%2B-blue">
  <img alt="OpenAI" src="https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white">
  <img alt="AWS Bedrock" src="https://img.shields.io/badge/AWS%20Bedrock-Claude-FF9900?logo=amazonaws&logoColor=white">
  <img alt="Ollama" src="https://img.shields.io/badge/Ollama-local-black">
</p>

**Werewolf Arena** is a benchmark for the social-reasoning skills of large language
models. It runs full games of the social-deduction game **Werewolf** in which every
player is an LLM, then records who deceived, who deduced, and who won. Villagers must
unmask the hidden werewolves through debate and voting; werewolves must blend in and
mislead. Because winning demands theory-of-mind, persuasion, and deception — not just
fact recall — Werewolf is a sharp probe of where today's models actually stand on social
intelligence.

This repository is a fork of Google's [Werewolf Arena](https://arxiv.org/abs/2407.13943)
research framework, extended for self-hosting and broader model coverage. The additions
in this fork are **local inference via [Ollama](https://ollama.com)**, **AWS Bedrock
(Claude) support**, a **pytest suite**, and **Docker / GHCR CI** for reproducible runs.

## ✨ Features

- **Full Werewolf game engine** — Seer, Doctor, Villager and Werewolf roles, night/day
  rounds, debate, bidding, synthetic voting, and win detection.
- **Model vs. model arena** — pit any villager model against any werewolf model and run
  every combination to collect head-to-head win rates.
- **Three inference backends** — OpenAI (`gpt-*`), AWS Bedrock for Claude
  (`claude3-*`), and local Ollama models (`deepseek-r1`, `llama2`, `qwen`).
- **Resumable games** — interrupted or failed games can be reloaded from their saved
  state and continued.
- **Interactive web viewer** — a TypeScript replay UI to inspect each player's private
  reasoning, bids, votes and prompts after a game finishes.
- **Reproducible evaluation** — eval mode writes a CSV of every game's models, winner,
  and log directory for later analysis.

## 📦 Installation

Requires **Python 3.8+**. For the web viewer you'll also need **Node.js / npm**.

```bash
# 1. Clone
git clone https://github.com/cajias/werewolf_arena.git
cd werewolf_arena

# 2. Create and activate a virtual environment
python3 -m venv ./venv
source ./venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configure a model backend

Pick at least one of the following.

```bash
# OpenAI (gpt4, gpt4o, gpt3.5)
export OPENAI_API_KEY=<your-api-key>

# AWS Bedrock (claude3-opus, claude3-sonnet, claude3-haiku)
#   configure standard AWS credentials (e.g. via `aws configure`)

# Ollama (deepseek-r1, llama2, qwen) — runs locally, no key required
#   install from https://ollama.com and `ollama serve`
#   see OLLAMA_SETUP.md for details
```

## 🚀 Usage

Games are launched through `main.py`. Models are selected with the short keys
`gpt4`, `gpt4o`, `gpt3.5`, `claude3-opus`, `claude3-sonnet`, `claude3-haiku`,
`deepseek-r1`, `llama2`, `qwen`.

```bash
# Run a single game: GPT-4o villagers vs. Claude 3 Haiku werewolves
python3 main.py --run --v_models=gpt4o --w_models=claude3-haiku

# Run a fully local game with Ollama (no API keys)
python3 main.py --run --v_models=qwen --w_models=llama2

# Evaluate every model combination, 5 games each
python3 main.py --eval --num_games=5 --v_models=gpt4o,gpt4 --w_models=claude3-haiku,qwen

# Arena mode: only play games where villager and werewolf models differ
python3 main.py --eval --arena --num_games=5 --v_models=gpt4o --w_models=qwen

# Resume previously failed games (directories listed in werewolf/runner.py)
python3 main.py --resume
```

Useful flags: `--num_games` (games per matchup in eval), `--threads` (parallel game
threads), `--arena` (skip same-model matchups). Game logs are written to `logs/` and
eval results to `logs/eval_results_<timestamp>.csv`.

### Launch the interactive viewer

![Werewolf Arena viewer](viewer.png)

Once a game has completed, replay it in the browser to explore every player's private
reasoning, bids and votes.

```bash
npm install
npm run start
# then open http://localhost:8080/?session_id=<your-session-id>
```

## 🗂️ Project Structure

```text
werewolf_arena/
├── main.py               # CLI entrypoint (absl flags → werewolf.runner.run)
├── werewolf/             # Core game engine package
│   ├── runner.py         # Run / eval / resume orchestration & model registry
│   ├── game.py           # GameMaster: round loop, debate, voting
│   ├── model.py          # Player roles, game state, observations
│   ├── apis.py           # OpenAI / Bedrock / Ollama inference backends
│   ├── lm.py             # Language-model call wrapper
│   ├── prompts.py        # Role and phase prompt templates
│   ├── config.py         # Player names, game-size constants
│   ├── analysis.py       # Post-game analysis helpers
│   ├── logging.py        # Save / load game state
│   └── utils.py          # Shared helpers
├── index.ts              # TypeScript source for the web viewer
├── index.html            # Viewer page
├── static/               # Player avatar assets for the viewer
├── examples/             # Example analysis script & experiment runner
├── tests/                # pytest suite (unit, integration, e2e)
└── test_ollama_manual.py # Manual Ollama connectivity check
```

## 🛠️ Development

```bash
# Run the test suite (excludes tests that need a live Ollama server)
pytest -m "not ollama_integration"

# Run the full suite, including Ollama integration tests
pytest

# With coverage
pytest --cov=werewolf

# Python lint
ruff check .
black --check .
mypy
pylint --disable=all --enable=duplicate-code main.py werewolf

# Markdown / formatting / TypeScript lint
npm run lint
npm run lint:ts

# Build the TypeScript viewer
npm run build
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`OLLAMA_SETUP.md`](OLLAMA_SETUP.md),
[`DOCKER_CI_SETUP.md`](DOCKER_CI_SETUP.md) and [`GHCR_USAGE.md`](GHCR_USAGE.md) for more.

## 🤝 Contributing

Contributions are welcome. Fork the repo, create a feature branch, keep the test suite
green (`pytest -m "not ollama_integration"`) and lint clean (`ruff check . && black --check . && mypy && npm run lint`),
then open a pull request. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for details.

## 📄 License

Licensed under the **Apache License 2.0** — see [`LICENSE`](LICENSE). This project is a
fork of Google's Werewolf Arena; the original framework and paper
([arXiv:2407.13943](https://arxiv.org/abs/2407.13943)) are the work of Google LLC.
