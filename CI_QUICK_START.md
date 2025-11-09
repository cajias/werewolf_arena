# CI Quick Start - Ollama E2E Tests

This project includes automated CI testing with Ollama for running e2e tests without API keys.

## 🚀 Ready to Use!

The GitHub Actions workflow is **already configured** and will run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger (workflow_dispatch)

## What Happens in CI

```
┌─────────────────────────────────────────────┐
│  1. Unit Tests (2-3 min)                    │
│     ✓ Linting with ruff                     │
│     ✓ All tests without Ollama              │
├─────────────────────────────────────────────┤
│  2. Ollama Integration Tests (5-8 min)      │
│     ✓ Install Ollama                        │
│     ✓ Pull qwen:0.5b model                  │
│     ✓ Run manual integration test           │
│     ✓ Run all tests including Ollama        │
├─────────────────────────────────────────────┤
│  3. Docker Build (Optional - main only)     │
│     ✓ Build Docker image                    │
│     ✓ Push to Docker Hub                    │
└─────────────────────────────────────────────┘
```

## First Time Setup (One-Time)

### No Setup Required! 🎉

The workflow uses **GitHub Container Registry (ghcr.io)** which:
- ✅ Automatically available with your GitHub repo
- ✅ No external accounts needed
- ✅ No secrets to configure
- ✅ Free for public and private repos
- ✅ Integrated with GitHub permissions

The workflow will automatically publish Docker images to `ghcr.io/YOUR_USERNAME/YOUR_REPO` on pushes to main or develop branches.

## Running Tests Locally

### Option 1: Mocked Tests (No Setup)
```bash
# Run all tests with mocked Ollama responses
python3 -m pytest tests/test_e2e_ollama.py -v

# ✓ Works immediately, no Ollama needed
```

### Option 2: Real Ollama Integration
```bash
# Install Ollama (one-time)
curl -fsSL https://ollama.com/install.sh | sh

# Start server
ollama serve &

# Pull model
ollama pull qwen:0.5b

# Run tests
python3 test_ollama_manual.py
python3 -m pytest tests/ -v
```

### Option 3: Docker (Local Build)
```bash
# Build image locally
docker build -f Dockerfile.ollama -t werewolf-test .

# Run tests
docker run --rm werewolf-test
```

### Option 4: Docker (Pull from GitHub)
```bash
# Pull pre-built image from GitHub Container Registry
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest

# Run tests
docker run --rm ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

Note: Replace `YOUR_USERNAME/YOUR_REPO` with your GitHub username and repository name.

## Selective Test Execution

```bash
# Run only fast unit tests (skip Ollama integration)
python3 -m pytest -m "not ollama_integration"

# Run only Ollama integration tests
python3 -m pytest -m "ollama_integration"

# Run only fast tests
python3 -m pytest -m "not slow"

# Skip all integration tests
python3 -m pytest tests/test_game.py tests/test_model.py
```

## CI Workflow Files

- `.github/workflows/test-with-ollama.yml` - Main CI workflow
- `Dockerfile.ollama` - Docker image for testing
- `.dockerignore` - Files to exclude from Docker build
- `test_ollama_manual.py` - Manual test script

## Published Docker Images

After pushing to main or develop, Docker images are automatically published to:

```
ghcr.io/YOUR_USERNAME/YOUR_REPO:latest        # Latest from main
ghcr.io/YOUR_USERNAME/YOUR_REPO:main          # Main branch
ghcr.io/YOUR_USERNAME/YOUR_REPO:develop       # Develop branch
ghcr.io/YOUR_USERNAME/YOUR_REPO:main-abc1234  # Specific commit
```

### Pulling Images

```bash
# Public repo (no auth needed)
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest

# Private repo (need GitHub token)
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO:latest
```

## Monitoring CI

### Check Workflow Status
1. Go to your repo on GitHub
2. Click "Actions" tab
3. See recent workflow runs

### Typical CI Times
- **Unit tests**: 2-3 minutes
- **Ollama integration**: 5-8 minutes
- **Docker build** (if enabled): 10-15 minutes
- **Total**: ~8-12 minutes per run

### Cost (GitHub Actions Free Tier)
- 2,000 minutes/month free
- ~8 min per run = ~250 runs/month free
- More than enough for most projects!

## Troubleshooting

### CI Fails: "Ollama not responding"
- Increase sleep time in workflow
- Check Ollama logs in CI output

### CI Fails: "Out of disk space"
- Using too large model
- Switch to `qwen:0.5b` (only ~400MB)

### Tests Pass Locally but Fail in CI
- Check Python version (CI uses 3.11)
- Check dependency versions
- Review CI logs for specific errors

### Docker Build Fails
- Check `.dockerignore` isn't excluding needed files
- Verify Dockerfile.ollama syntax
- Check CI has enough disk space

## Advanced: Custom Models in CI

To use different models in CI, edit `.github/workflows/test-with-ollama.yml`:

```yaml
- name: Pull custom model
  run: |
    ollama pull llama2:7b  # Change this line
```

**Warning**: Larger models = longer CI times and more disk space

## Files Created

```
werewolf_arena/
├── .github/
│   └── workflows/
│       └── test-with-ollama.yml    # CI workflow
├── .dockerignore                    # Docker build exclusions
├── Dockerfile.ollama                # Docker image definition
├── test_ollama_manual.py           # Manual test script
├── OLLAMA_SETUP.md                 # Detailed Ollama guide
├── DOCKER_CI_SETUP.md              # Detailed Docker/CI guide
└── CI_QUICK_START.md               # This file
```

## Next Steps

1. ✅ Push your code to GitHub
2. ✅ Watch the workflow run in Actions tab
3. (Optional) Set up Docker Hub for image publishing
4. (Optional) Customize model or workflow as needed

## Support

- **Ollama Issues**: See `OLLAMA_SETUP.md`
- **Docker Issues**: See `DOCKER_CI_SETUP.md`
- **General Testing**: See `README.md`

## Summary

✅ **Zero setup required** for basic CI
✅ **Automatic** e2e testing with Ollama
✅ **No API keys** needed
✅ **Free** on GitHub Actions (2k min/month)
✅ **Fast** runs (8-12 minutes)
✅ **Reproducible** with Docker option

Just push and let CI do the work!
