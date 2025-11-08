# Docker & CI Setup for Ollama Tests

This guide explains how to run Ollama e2e tests in CI using Docker.

## Architecture

```
┌─────────────────────────────────────────┐
│         GitHub Actions Runner           │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │     Docker Container              │  │
│  │                                   │  │
│  │  ├── Ollama Server (background)  │  │
│  │  ├── qwen:0.5b model             │  │
│  │  ├── Python 3.11                 │  │
│  │  └── Werewolf Arena Tests        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Quick Start

### Option 1: Use GitHub Actions (Recommended)

The `.github/workflows/test-with-ollama.yml` workflow automatically:
1. Runs unit tests without Ollama
2. Runs e2e tests with Ollama installed directly on the runner
3. (Optional) Builds and tests in Docker
4. (On main branch) Publishes Docker image to Docker Hub

**No additional setup required!** Just push to GitHub.

### Option 2: Build Docker Image Locally

```bash
# Build the image
docker build -f Dockerfile.ollama -t werewolf-arena-ollama .

# Run all tests
docker run --rm werewolf-arena-ollama

# Run specific tests
docker run --rm werewolf-arena-ollama /app/run_tests.sh tests/test_e2e_ollama.py -v

# Run with interactive shell
docker run --rm -it werewolf-arena-ollama /bin/bash
```

### Option 3: Pull Pre-built Image from Docker Hub

Once published, you can use the pre-built image:

```bash
# Pull the image
docker pull yourusername/werewolf-arena-ollama:latest

# Run tests
docker run --rm yourusername/werewolf-arena-ollama
```

## GitHub Actions Workflow

The workflow has 4 jobs:

### 1. `test-unit` - Fast Unit Tests
- Runs without Ollama
- Checks linting with ruff
- Runs all tests except Ollama integration
- **Fast**: ~2-3 minutes

### 2. `test-ollama-integration` - Real E2E Tests
- Installs Ollama directly on the runner
- Pulls qwen:0.5b model (~400MB)
- Runs manual test script
- Runs all tests including Ollama integration
- **Medium**: ~5-8 minutes (includes model download)

### 3. `test-docker` - Docker Testing (Manual)
- Only runs on manual workflow dispatch
- Builds Docker image
- Runs tests inside the container
- **Slow**: ~10-15 minutes (includes building image)

### 4. `publish-docker-image` - Publish to Docker Hub
- Only runs on pushes to main branch
- Requires Docker Hub credentials
- Publishes image for others to use
- **Fast**: ~5 minutes (uses cache)

## Setting Up Docker Hub Publishing

To publish the Docker image to Docker Hub:

### 1. Create Docker Hub Account
- Go to https://hub.docker.com
- Create an account (free tier is fine)

### 2. Create Access Token
1. Go to Account Settings → Security
2. Click "New Access Token"
3. Name it "GitHub Actions"
4. Copy the token (you won't see it again!)

### 3. Add GitHub Secrets
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add two secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: The access token from step 2

### 4. Push to Main Branch
The image will automatically build and publish!

## Docker Image Details

### Base Image
- `python:3.11-slim` - Minimal Debian-based Python image

### What's Included
- Python 3.11
- Ollama (latest version)
- All Python dependencies from requirements.txt
- Werewolf Arena code
- Pre-configured startup script

### Image Size
- Base: ~500MB
- With qwen:0.5b model: ~900MB
- With larger models: Varies (deepseek-r1:70b = ~40GB)

### Environment Variables
- `OLLAMA_HOST`: `0.0.0.0:11434`
- `OLLAMA_MODELS`: `/root/.ollama/models`

## Advanced Usage

### Using Different Models

```bash
# Build with custom model
docker run --rm -it werewolf-arena-ollama /bin/bash
> ollama pull llama2:7b
> python3 main.py --run --v_models=llama2 --w_models=llama2
```

### Custom Dockerfile

If you want to bake a model into the image:

```dockerfile
FROM python:3.11-slim

# ... (existing setup) ...

# Pre-download model (increases image size!)
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen:0.5b && \
    pkill ollama

# ... (rest of dockerfile) ...
```

**Trade-off**: Faster test startup vs larger image size

### Running Specific Game Configurations

```bash
# Run evaluation with multiple models
docker run --rm werewolf-arena-ollama /bin/bash -c "
  ollama serve &
  sleep 5
  python3 main.py --eval --num_games=5 --v_models=qwen --w_models=qwen
"
```

### Debugging in Docker

```bash
# Start interactive shell
docker run --rm -it werewolf-arena-ollama /bin/bash

# Inside container:
ollama serve &
sleep 5
ollama list
python3 test_ollama_manual.py
python3 -m pytest tests/test_e2e_ollama.py -xvs
```

## CI Performance Optimization

### Strategy 1: Direct Ollama Install (Fastest)
```yaml
- name: Install Ollama
  run: curl -fsSL https://ollama.com/install.sh | sh
```
- ✅ Fast setup (~30 seconds)
- ✅ Native performance
- ❌ No isolation

### Strategy 2: Docker with Cached Image (Balanced)
```yaml
- name: Pull pre-built image
  run: docker pull user/werewolf-arena-ollama:latest
```
- ✅ Good isolation
- ✅ Reproducible environment
- ❌ Slower startup (~2-3 minutes)

### Strategy 3: Build Docker Each Time (Slowest)
```yaml
- name: Build Docker image
  run: docker build -f Dockerfile.ollama -t test .
```
- ✅ Always fresh
- ❌ Very slow (~10-15 minutes)
- Use only for testing Docker build itself

**Recommendation**: Use Strategy 1 (direct install) for regular CI, Strategy 2 (pre-built image) for reproducibility.

## Caching Strategies

### Model Caching
```yaml
- name: Cache Ollama models
  uses: actions/cache@v4
  with:
    path: ~/.ollama/models
    key: ollama-models-${{ hashFiles('OLLAMA_MODELS.txt') }}
```

### Docker Layer Caching
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Troubleshooting

### "Ollama server not responding"

**Problem**: Ollama didn't start in time

**Solution**: Increase sleep time
```yaml
- run: |
    ollama serve &
    sleep 10  # Increase from 5 to 10
```

### "Out of disk space"

**Problem**: Models are large

**Solutions**:
1. Use smaller models (qwen:0.5b instead of deepseek-r1)
2. Clean up after tests:
```bash
ollama rm qwen:0.5b
```

### "Tests timeout in CI"

**Problem**: Model inference is slow

**Solutions**:
1. Use faster models
2. Increase timeout:
```yaml
- run: python3 -m pytest --timeout=600  # 10 minute timeout
```
3. Reduce test complexity

### "Docker build fails"

**Problem**: Network issues during Ollama install

**Solution**: Add retry logic
```dockerfile
RUN for i in 1 2 3; do \
      curl -fsSL https://ollama.com/install.sh | sh && break || sleep 10; \
    done
```

## Cost Analysis

### GitHub Actions (Free Tier)
- 2,000 minutes/month for free
- Our workflow: ~8 minutes per run
- **Can run ~250 times/month for free**

### Paid Runners
- Standard: $0.008/minute
- Our workflow: ~$0.064 per run
- 100 runs/month: ~$6.40

### Self-Hosted Runners (Best for Heavy Use)
- Free (you provide hardware)
- Can run unlimited tests
- Can pre-load models for faster tests

## Comparison: CI Strategies

| Strategy | Setup Time | Run Time | Cost | Reproducibility |
|----------|-----------|----------|------|-----------------|
| Direct Ollama | 30s | 5-8 min | Free | Medium |
| Pre-built Docker | 2 min | 6-9 min | Free | High |
| Build Docker | 10 min | 12-15 min | Free | Very High |
| Self-hosted | 1 hour (once) | 2-3 min | $0 | Very High |

## Example: Complete CI Run

```bash
# What happens when you push to main:

1. GitHub Actions starts
2. Spins up Ubuntu runner
3. Checks out code
4. Installs Python 3.11
5. Installs dependencies (30s)
6. Runs linter (10s)
7. Runs unit tests (30s)
8. Installs Ollama (30s)
9. Starts Ollama server (5s)
10. Pulls qwen:0.5b (2-3 min)
11. Runs manual test (30s)
12. Runs all tests (1-2 min)
13. (On main) Builds Docker image (5 min)
14. (On main) Pushes to Docker Hub (1 min)

Total: ~8-12 minutes
```

## Best Practices

1. **Use Small Models for CI**: qwen:0.5b is perfect
2. **Cache Models**: Save ~2-3 minutes per run
3. **Parallel Jobs**: Run unit tests while Ollama installs
4. **Skip on Draft PRs**: Save CI minutes
5. **Manual Trigger for Docker**: Build images only when needed

## Next Steps

1. ✅ Workflow is ready to use
2. Set up Docker Hub secrets (optional)
3. Push to trigger first run
4. Monitor CI times and optimize as needed

## Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Hub](https://hub.docker.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
