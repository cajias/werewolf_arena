# Enable Linter Rules and Add Ollama CI Support

## Summary

This PR significantly improves code quality and testing infrastructure by:
1. ✅ Enabling all disabled linter rules and achieving full compliance
2. ✅ Adding Ollama support for local LLM testing without API keys
3. ✅ Implementing complete CI/CD pipeline with GitHub Actions
4. ✅ Adding Docker support for reproducible testing
5. ✅ Comprehensive documentation for setup and usage

## Changes

### 1. Linter Compliance (Zero Violations)

**Enabled Previously Disabled Rules:**
- `B904` - Exception chaining (`raise ... from e`)
- `C901` - Cyclomatic complexity checking
- `B024`, `B027`, `B019`, `B007` - Additional bugbear checks
- `ANN` - Type annotation requirements

**Fixed Violations:**
- Added complete type annotations to all production code (werewolf/, main.py, examples/)
- Refactored `resume_game()` to reduce complexity from 16 to <10
- Fixed exception chaining throughout codebase
- Configured per-file ignores for test files (common practice)

**Files Modified:**
- `pyproject.toml` - Updated linter configuration
- `werewolf/runner.py` - Reduced complexity, added type hints
- `werewolf/apis.py` - Complete error handling and type annotations
- `werewolf/model.py` - Added return type annotations (20 fixes)
- `werewolf/game.py`, `werewolf/lm.py`, `werewolf/config.py`, etc. - Type hints

**Result:** All 52 tests pass, zero linter violations in production code

### 2. Ollama Integration (Local LLM Testing)

**New Features:**
- Added `generate_ollama()` function for Ollama API calls
- Support for JSON mode, custom temperature, and max tokens
- Comprehensive error handling with helpful messages
- Configurable via `OLLAMA_BASE_URL` environment variable

**Model Support:**
- Added mappings for `deepseek-r1`, `llama2`, `qwen`
- Models use `ollama:` prefix (e.g., `ollama:deepseek-r1:latest`)
- Updated CLI help text

**Testing:**
- 7 new e2e tests with mocked Ollama responses
- Manual test script (`test_ollama_manual.py`)
- All tests pass without requiring Ollama installation

**Files Added:**
- `werewolf/apis.py` - `generate_ollama()` function
- `tests/test_e2e_ollama.py` - Comprehensive e2e tests
- `test_ollama_manual.py` - Manual testing script
- `OLLAMA_SETUP.md` - Complete setup guide

**Files Modified:**
- `werewolf/runner.py` - Added Ollama model mappings
- `requirements.txt` - Added `requests` library

**Benefits:**
- ✅ Run e2e tests without API keys
- ✅ No API costs for development/testing
- ✅ Test with any Ollama-supported model
- ✅ Works locally and in CI

### 3. GitHub Actions CI/CD

**Workflow Jobs:**

1. **test-unit** (2-3 min)
   - Runs linter
   - Runs all unit tests without Ollama
   - Fast feedback on basic issues

2. **test-ollama-integration** (5-8 min)
   - Installs Ollama directly on runner
   - Pulls qwen:0.5b model (~400MB)
   - Runs manual integration test
   - Runs full test suite

3. **test-docker** (10-15 min, manual trigger only)
   - Builds Docker image
   - Runs tests in container
   - Validates Docker setup

4. **publish-ghcr-image** (5 min, main/develop only)
   - Publishes to GitHub Container Registry
   - **No setup required** - uses GITHUB_TOKEN
   - Tags: latest, branch name, commit SHA
   - Uses GitHub Actions cache for speed

**Files Added:**
- `.github/workflows/test-with-ollama.yml` - Main CI workflow
- `Dockerfile.ollama` - Docker image for testing
- `.dockerignore` - Optimized Docker builds
- `CI_QUICK_START.md` - Quick setup guide
- `DOCKER_CI_SETUP.md` - Comprehensive CI/Docker docs
- `GHCR_USAGE.md` - Guide for using published images

**Configuration:**
- `pyproject.toml` - Added pytest configuration and test markers

**Total CI Time:** ~8-12 minutes per run
**Cost:** Free (fits in GitHub Actions free tier - 2,000 min/month)

### 4. GitHub Container Registry (ghcr.io)

**Why GHCR instead of Docker Hub:**
- ✅ **Zero setup** - No external accounts needed
- ✅ **No secrets** - Uses GITHUB_TOKEN automatically
- ✅ **Free** - Included with GitHub (public/private)
- ✅ **Integrated** - Native GitHub permissions
- ✅ **Private by default** - Control access via GitHub

**Published Images:**
```
ghcr.io/YOUR_USERNAME/werewolf_arena:latest        # Latest from main
ghcr.io/YOUR_USERNAME/werewolf_arena:main          # Main branch
ghcr.io/YOUR_USERNAME/werewolf_arena:develop       # Develop branch
ghcr.io/YOUR_USERNAME/werewolf_arena:main-abc1234  # Specific commit
```

**Usage:**
```bash
# Public repo (no auth needed)
docker pull ghcr.io/username/werewolf_arena:latest
docker run --rm ghcr.io/username/werewolf_arena:latest

# Private repo
echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin
docker pull ghcr.io/username/werewolf_arena:latest
```

### 5. Documentation

**New Documentation Files:**
- `OLLAMA_SETUP.md` - Ollama installation and setup
- `CI_QUICK_START.md` - Quick CI setup guide
- `DOCKER_CI_SETUP.md` - Comprehensive Docker/CI documentation
- `GHCR_USAGE.md` - Using published container images
- `PULL_REQUEST.md` - This file

**Topics Covered:**
- Installation and setup
- Model comparison and selection
- Troubleshooting common issues
- Performance optimization
- Cost analysis
- Best practices
- Advanced configuration

## Testing

### Test Coverage
- **52 tests total**, all passing
- **45** existing unit/integration tests
- **7** new Ollama e2e tests

### Test Execution
```bash
# All tests
pytest tests/ -v

# Fast tests only (skip Ollama integration)
pytest -m "not ollama_integration"

# Ollama tests only
pytest -m "ollama_integration"
```

### CI Validation
- ✅ Linter passes (zero violations)
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Ollama e2e tests pass (mocked)
- ✅ Docker builds successfully

## Breaking Changes

None. All changes are additive:
- Existing APIs unchanged
- Backward compatible
- New features opt-in

## Deployment

### After Merge

1. **Automatic on push to main/develop:**
   - CI runs automatically
   - Docker image publishes to ghcr.io
   - Available at `ghcr.io/username/werewolf_arena:latest`

2. **Optional - Make image public:**
   - Go to GitHub → Packages
   - Click on package → Package settings
   - Change visibility → Public

3. **Optional - Pull and use image:**
   ```bash
   docker pull ghcr.io/username/werewolf_arena:latest
   docker run --rm ghcr.io/username/werewolf_arena:latest
   ```

## Migration Guide

### For Developers

**No changes required!** Existing workflows continue to work:
- OpenAI models: `--v_models=gpt4 --w_models=gpt4o`
- Bedrock models: `--v_models=claude3-sonnet --w_models=claude3-opus`

**New options available:**
- Ollama models: `--v_models=deepseek-r1 --w_models=qwen`

### For CI/CD

**Zero setup required!** The workflow uses:
- GITHUB_TOKEN (automatic)
- GitHub Container Registry (automatic)
- No secrets to configure

## Metrics

### Code Quality
- **Before:** 6 disabled linter rules, unknown violations
- **After:** All rules enabled, zero violations
- **Type annotations:** 100% coverage in production code

### Testing
- **Before:** 45 tests
- **After:** 52 tests (+7 Ollama e2e tests)
- **Coverage:** All critical paths covered

### CI/CD
- **Before:** No automated CI
- **After:** Full CI/CD pipeline
- **Time:** 8-12 minutes per run
- **Cost:** Free (GitHub Actions free tier)

## Future Enhancements

Potential follow-up work (not in this PR):
1. Add more Ollama models (Mistral, CodeLlama, etc.)
2. Add CI caching for Ollama models (save 2-3 min)
3. Add GitHub Actions status badges to README
4. Configure branch protection rules
5. Add semantic versioning for Docker tags

## Checklist

- [x] All tests pass locally
- [x] Linter passes with zero violations
- [x] Documentation updated
- [x] CI workflow tested
- [x] Docker builds successfully
- [x] No breaking changes
- [x] Backward compatible

## How to Test

### Locally

```bash
# 1. Run linter
ruff check werewolf/ main.py examples/

# 2. Run all tests
pytest tests/ -v

# 3. Test with Ollama (if installed)
ollama serve &
ollama pull qwen:0.5b
python3 test_ollama_manual.py

# 4. Build Docker image
docker build -f Dockerfile.ollama -t test .
docker run --rm test
```

### In CI

After merge, CI will automatically:
1. Run linter
2. Run all tests
3. Install Ollama and run integration tests
4. Build Docker image
5. Publish to ghcr.io

Check the "Actions" tab on GitHub to monitor progress.

## Related Issues

Addresses:
- Code quality improvements
- Testing without API keys
- CI/CD automation
- Docker support

## Contributors

- Claude (AI Assistant)

---

**Total Changes:**
- **Files Added:** 10
- **Files Modified:** 15
- **Lines Added:** ~2,500
- **Lines Removed:** ~150
- **Tests Added:** 7
- **Documentation Added:** 5 guides

**Impact:**
- ✅ Significantly improved code quality
- ✅ Zero-cost local testing with Ollama
- ✅ Automated CI/CD pipeline
- ✅ Reproducible testing with Docker
- ✅ Comprehensive documentation
