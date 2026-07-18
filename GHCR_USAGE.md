# Using Pre-built Docker Images from GitHub Container Registry

This project automatically publishes Docker images to GitHub Container Registry (ghcr.io) on every push to `main` or `develop` branches.

## Quick Start

### For Public Repositories

```bash
# Pull the latest image
docker pull ghcr.io/YOUR_USERNAME/werewolf_arena:latest

# Run all tests
docker run --rm ghcr.io/YOUR_USERNAME/werewolf_arena:latest

# Run specific tests
docker run --rm ghcr.io/YOUR_USERNAME/werewolf_arena:latest \
  /app/run_tests.sh tests/test_e2e_ollama.py -v

# Interactive shell
docker run --rm -it ghcr.io/YOUR_USERNAME/werewolf_arena:latest /bin/bash
```

### For Private Repositories

```bash
# 1. Create a GitHub Personal Access Token
# Go to: Settings → Developer settings → Personal access tokens → Tokens (classic)
# Click "Generate new token" with these scopes:
#   - read:packages

# 2. Login to GitHub Container Registry
echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# 3. Pull the image
docker pull ghcr.io/YOUR_USERNAME/werewolf_arena:latest

# 4. Run tests
docker run --rm ghcr.io/YOUR_USERNAME/werewolf_arena:latest
```

## Available Tags

Images are tagged automatically based on the branch and commit:

| Tag               | Description                  | Example                             |
| ----------------- | ---------------------------- | ----------------------------------- |
| `latest`          | Latest from main branch      | `ghcr.io/user/repo:latest`          |
| `main`            | Latest from main branch      | `ghcr.io/user/repo:main`            |
| `develop`         | Latest from develop branch   | `ghcr.io/user/repo:develop`         |
| `main-abc1234`    | Specific commit from main    | `ghcr.io/user/repo:main-abc1234`    |
| `develop-xyz5678` | Specific commit from develop | `ghcr.io/user/repo:develop-xyz5678` |

### Using Specific Tags

```bash
# Use a specific branch
docker pull ghcr.io/YOUR_USERNAME/werewolf_arena:develop

# Use a specific commit (for reproducibility)
docker pull ghcr.io/YOUR_USERNAME/werewolf_arena:main-abc1234
```

## Running Games with Pre-built Image

### Quick Test Game

```bash
docker run --rm ghcr.io/YOUR_USERNAME/werewolf_arena:latest \
  /bin/bash -c "
    ollama serve &
    sleep 5
    ollama pull qwen:0.5b
    python3 main.py --run --v_models=qwen --w_models=qwen
  "
```

### Evaluation Mode

```bash
docker run --rm ghcr.io/YOUR_USERNAME/werewolf_arena:latest \
  /bin/bash -c "
    ollama serve &
    sleep 5
    ollama pull qwen:0.5b
    python3 main.py --eval --num_games=5 --v_models=qwen --w_models=qwen
  "
```

## Making Images Public

By default, images pushed to GitHub Container Registry are private. To make them public:

1. Go to your GitHub profile
2. Click "Packages" tab
3. Click on the `werewolf_arena` package
4. Click "Package settings"
5. Under "Danger Zone", click "Change visibility"
6. Select "Public"
7. Confirm the change

**Benefits of public images:**

- ✅ Anyone can pull without authentication
- ✅ Easier for collaborators
- ✅ Can be used in public CI/CD pipelines
- ✅ Discoverable on GitHub

**Keep private if:**

- ❌ Contains proprietary code
- ❌ Not ready for public use
- ❌ Want to control access

## Viewing Package Details

### On GitHub Web

1. Go to your repository
2. Click "Packages" in the right sidebar
3. View downloads, tags, and metadata

### Using GitHub CLI

```bash
# List packages for your user
gh api user/packages --jq '.[].name'

# Get package details
gh api user/packages/container/werewolf_arena
```

## Deleting Old Images

To save space, you can delete old images:

### Via Web Interface

1. Go to the package page
2. Click on a specific version
3. Click "Delete version"

### Via API

```bash
# Delete a specific version
gh api --method DELETE \
  /user/packages/container/werewolf_arena/versions/VERSION_ID
```

## Using in Other CI/CD Systems

### GitHub Actions (Other Repos)

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/YOUR_USERNAME/werewolf_arena:latest
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    steps:
      - name: Run tests
        run: pytest tests/
```

### GitLab CI

```yaml
test:
  image: ghcr.io/YOUR_USERNAME/werewolf_arena:latest
  script:
    - pytest tests/
  before_script:
    - echo $CI_GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin
```

### CircleCI

```yaml
version: 2.1
jobs:
  test:
    docker:
      - image: ghcr.io/YOUR_USERNAME/werewolf_arena:latest
        auth:
          username: $GITHUB_USERNAME
          password: $GITHUB_TOKEN
    steps:
      - run: pytest tests/
```

## Troubleshooting

### "authentication required"

**Problem**: Trying to pull a private image without authentication

**Solution**:

```bash
# Create a GitHub Personal Access Token with read:packages scope
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### "image not found"

**Problem**: Image hasn't been published yet

**Solutions**:

1. Check if CI workflow completed successfully
2. Verify you pushed to `main` or `develop` branch
3. Check the "Packages" tab on GitHub
4. Ensure workflow has `packages: write` permission

### "no space left on device"

**Problem**: Too many old images taking up space

**Solution**:

```bash
# Clean up old images
docker system prune -a

# Remove specific image
docker rmi ghcr.io/YOUR_USERNAME/werewolf_arena:old-tag
```

### "denied: installation not allowed"

**Problem**: Repository doesn't have package permissions

**Solution**:

1. Go to repo Settings → Actions → General
2. Under "Workflow permissions"
3. Select "Read and write permissions"
4. Save changes

## Best Practices

1. **Use specific tags for production**: Don't use `latest` in production, use commit-specific tags for reproducibility

2. **Clean up old images**: Delete old versions regularly to save space

3. **Use semantic versioning**: Consider tagging releases with versions like `v1.0.0`

4. **Document image usage**: Add instructions in your README

5. **Test images before tagging**: Pull and test images before promoting to `latest`

## Advanced: Custom Tags

To add custom tags (like version numbers), update the workflow:

```yaml
- name: Extract metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/${{ github.repository }}
    tags: |
      type=ref,event=branch
      type=sha,prefix={{branch}}-
      type=raw,value=latest,enable={{is_default_branch}}
      type=semver,pattern={{version}}        # Add this
      type=semver,pattern={{major}}.{{minor}} # Add this
```

Then create Git tags to trigger versioned builds:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Summary

✅ **Zero setup** - Works automatically with GitHub
✅ **Free** - Included with GitHub (public/private)
✅ **Integrated** - Native permissions and access control
✅ **Fast** - Cached layers for quick pulls
✅ **Secure** - Private by default, uses GitHub auth

Replace `YOUR_USERNAME` and `werewolf_arena` with your actual GitHub username and repository name.
