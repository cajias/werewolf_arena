# Examples

This directory contains example configurations and scripts for running Werewolf Arena games.

## Quick Start Examples

### 1. Single Game with GPT-4 and Gemini

Run a single game with Gemini Pro 1.5 as villagers and GPT-4 as werewolves:

```bash
python3 main.py --run --v_models=pro1.5 --w_models=gpt4
```

### 2. Evaluation with Multiple Models

Run 10 games comparing different model combinations:

```bash
python3 main.py --eval --num_games=10 --v_models=pro1.5,flash --w_models=gpt4,gpt4o
```

This will run games with all combinations:

- Gemini Pro 1.5 villagers vs GPT-4 werewolves
- Gemini Pro 1.5 villagers vs GPT-4o werewolves
- Gemini Flash villagers vs GPT-4 werewolves
- Gemini Flash villagers vs GPT-4o werewolves

### 3. Arena Mode

Run games only where villagers and werewolves use different models:

```bash
python3 main.py --eval --arena --num_games=5 --v_models=pro1.5,flash --w_models=gpt4,gpt4o
```

### 4. Resume Failed Games

If games failed or were interrupted, resume them:

```bash
python3 main.py --resume
```

Note: The games to resume must be configured in `werewolf/runner.py` by setting the `RESUME_DIRECTORIES` variable.

## Available Models

### OpenAI Models

- `gpt4` - GPT-4 Turbo (gpt-4-turbo-2024-04-09)
- `gpt4o` - GPT-4o (gpt-4o-2024-05-13)
- `gpt3.5` - GPT-3.5 Turbo (gpt-3.5-turbo-0125)

### Google Gemini Models

- `pro1.5` - Gemini 1.5 Pro (gemini-1.5-pro-preview-0514)
- `flash` - Gemini 1.5 Flash (gemini-1.5-flash-001)
- `pro1` - Gemini Pro 1.0 (gemini-pro)

## Configuration Options

### Command-Line Flags

- `--run` - Run a single game
- `--eval` - Run multiple games for evaluation
- `--resume` - Resume previously failed games
- `--num_games=N` - Number of games to run (default: 2)
- `--v_models=MODEL1,MODEL2` - Models for villagers (comma-separated)
- `--w_models=MODEL1,MODEL2` - Models for werewolves (comma-separated)
- `--arena` - Only run games with different models for villagers and werewolves
- `--threads=N` - Number of threads for parallel execution (default: 2)

## Game Logs and Viewer

After running games, logs are saved in timestamped directories (e.g., `session_20240610_084702`).

To view a completed game in the interactive viewer:

1. Install Node.js dependencies:

   ```bash
   npm install
   ```

2. Start the viewer:

   ```bash
   npm run start
   ```

3. Open in your browser:
   ```
   http://localhost:8080/?session_id=session_20240610_084702
   ```

## Example Scripts

See the `run_experiments.sh` file for a sample batch experiment script.

## Tips

1. **API Keys**: Make sure your API keys are set:
   - OpenAI: `export OPENAI_API_KEY=your_key`
   - GCP/Gemini: Run `gcloud auth application-default login`

2. **Parallel Execution**: Use the `--threads` flag to speed up player actions:

   ```bash
   python3 main.py --run --v_models=pro1.5 --w_models=gpt4 --threads=4
   ```

3. **Reproducibility**: Games use random player assignments. For reproducible results, you may want to run multiple games and analyze the aggregate statistics.

4. **Cost Management**: Running many games with GPT-4 can be expensive. Start with smaller evaluations or use GPT-3.5 for testing.
