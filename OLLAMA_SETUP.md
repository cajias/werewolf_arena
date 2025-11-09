# Ollama Integration Guide

This guide explains how to use Ollama for local LLM testing without API keys.

## Why Use Ollama?

- ✅ **No API keys required** - Run models locally
- ✅ **No API costs** - Free to use
- ✅ **Fast iteration** - Test changes immediately
- ✅ **Privacy** - All data stays on your machine
- ✅ **Multiple models** - DeepSeek, Llama, Qwen, and more

## Quick Start

### 1. Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Or visit: https://ollama.com/download
```

### 2. Start Ollama Server

```bash
# Start the server (runs in background)
ollama serve
```

### 3. Pull a Model

```bash
# Small fast model (recommended for testing)
ollama pull qwen:0.5b

# Or use DeepSeek R1 (larger, more capable)
ollama pull deepseek-r1:latest

# Or Llama 2
ollama pull llama2:latest
```

### 4. Test the Integration

```bash
# Run manual test script
python3 test_ollama_manual.py

# Should output:
# ✓ Ollama connection successful!
# ✓ All Ollama tests passed!
```

### 5. Run a Game

```bash
# Single game with Qwen (fast)
python3 main.py --run --v_models=qwen --w_models=qwen

# Single game with DeepSeek R1 (better quality)
python3 main.py --run --v_models=deepseek-r1 --w_models=deepseek-r1

# Evaluation mode (multiple games)
python3 main.py --eval --num_games=3 --v_models=qwen --w_models=deepseek-r1
```

## Available Ollama Models

| Model Name | Command | Size | Speed | Quality |
|------------|---------|------|-------|---------|
| qwen | `--v_models=qwen` | ~0.5GB | ⚡⚡⚡ | ⭐⭐ |
| llama2 | `--v_models=llama2` | ~4GB | ⚡⚡ | ⭐⭐⭐ |
| deepseek-r1 | `--v_models=deepseek-r1` | ~40GB | ⚡ | ⭐⭐⭐⭐⭐ |

## Configuration

### Custom Ollama URL

If Ollama is running on a different host or port:

```bash
export OLLAMA_BASE_URL=http://192.168.1.100:11434
python3 main.py --run --v_models=qwen --w_models=qwen
```

### Model Tags

You can use specific model versions:

```bash
# Pull specific version
ollama pull qwen:0.5b
ollama pull deepseek-r1:7b
ollama pull llama2:13b

# Models are automatically mapped to :latest tag in the code
# But you can modify werewolf/runner.py to use specific versions
```

## Testing

### Mocked Tests (No Ollama Required)

```bash
# Run automated tests with mocked Ollama responses
python3 -m pytest tests/test_e2e_ollama.py -v

# These tests verify the integration works without requiring Ollama
```

### Real Tests (Ollama Required)

```bash
# Manual integration test
python3 test_ollama_manual.py

# Full test suite
python3 -m pytest tests/ -v
```

## Troubleshooting

### "Could not connect to Ollama server"

**Problem**: Ollama server is not running

**Solution**:
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve
```

### "The model may not be available"

**Problem**: Model not downloaded

**Solution**:
```bash
# List available models
ollama list

# Pull the model
ollama pull qwen:0.5b
```

### "API call timed out"

**Problem**: Model is too slow or prompt is too complex

**Solutions**:
- Use a smaller/faster model (qwen:0.5b instead of deepseek-r1)
- Reduce the number of debate turns in the game
- Increase hardware resources (CPU/RAM)

### Performance Issues

**Tips for better performance**:

1. **Use GPU acceleration** (if available):
   - Ollama automatically uses GPU when available
   - Check: `nvidia-smi` for NVIDIA GPUs

2. **Adjust model size**:
   ```bash
   # Faster but less capable
   ollama pull qwen:0.5b

   # Balanced
   ollama pull llama2:7b

   # Slower but more capable
   ollama pull deepseek-r1:70b
   ```

3. **Reduce parallelism**:
   ```bash
   # Run with fewer threads
   python3 main.py --run --threads=1 --v_models=qwen --w_models=qwen
   ```

## Comparison: Ollama vs Cloud APIs

| Feature | Ollama | OpenAI | AWS Bedrock |
|---------|--------|--------|-------------|
| Setup | Medium | Easy | Complex |
| Cost | Free | $$ per token | $$ per token |
| Speed | Depends on HW | Fast | Fast |
| Privacy | ✅ Local | ❌ Cloud | ❌ Cloud |
| Model Quality | Good | Excellent | Excellent |
| API Keys | ❌ Not needed | ✅ Required | ✅ Required |
| Best For | Dev/Testing | Production | Enterprise |

## Example: Complete Workflow

```bash
# 1. Install and setup
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull qwen:0.5b

# 2. Test integration
python3 test_ollama_manual.py

# 3. Run a quick game
python3 main.py --run --v_models=qwen --w_models=qwen

# 4. Run evaluation
python3 main.py --eval --num_games=5 --v_models=qwen,llama2 --w_models=qwen

# 5. View results
npm run start
# Open browser to http://localhost:8080/?session_id=<your_session>
```

## Advanced: Adding New Ollama Models

To add new Ollama models to the game:

1. Edit `werewolf/runner.py`:
```python
model_to_id = {
    # ... existing models ...
    "mistral": "ollama:mistral:latest",
    "codellama": "ollama:codellama:latest",
}
```

2. Update the CLI help text:
```python
_VILLAGER_MODELS = flags.DEFINE_list(
    "v_models",
    "",
    "... existing text ..., mistral, codellama",
)
```

3. Pull the model:
```bash
ollama pull mistral
```

4. Use it:
```bash
python3 main.py --run --v_models=mistral --w_models=codellama
```

## Resources

- **Ollama Website**: https://ollama.com
- **Ollama GitHub**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.com/library
- **Ollama API Docs**: https://github.com/ollama/ollama/blob/main/docs/api.md
