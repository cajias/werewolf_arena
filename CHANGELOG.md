# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with pytest
  - Unit tests for game logic (game.py)
  - Unit tests for player models (model.py)
  - Integration tests for game flow
  - Test coverage reporting with pytest-cov
- CHANGELOG.md to track version history
- Examples directory with sample game configurations
- Analysis module for game statistics and performance metrics
- pytest configuration and fixtures

### Changed
- Updated CI workflow to run automated tests with pytest
- Enhanced CI workflow with test coverage reporting
- Updated requirements.txt to include testing dependencies

### Fixed
- Code style improvements addressing some Ruff linting warnings

## [0.1.0] - 2024-11-06

### Added
- GitHub Actions CI workflow with Ruff linting
- Automated linting for code quality checks
- Import sorting validation

### Changed
- Set up Ruff linting configuration in pyproject.toml
- Fixed code style issues throughout the codebase

## [0.0.1] - 2024-06-10

### Added
- Initial release of Werewolf Arena
- Core game logic for running Werewolf games with LLMs
- Support for multiple LLM models:
  - OpenAI GPT models (GPT-3.5, GPT-4, GPT-4o)
  - Google Gemini models (Flash, Pro 1.0, Pro 1.5)
  - Anthropic Claude models (in requirements)
- Interactive web viewer for game logs
  - View player reasoning, bids, votes, and prompts
  - Navigate game history visually
- Command-line interface for running games:
  - Single game mode (`--run`)
  - Evaluation mode (`--eval`) for running multiple games
  - Resume failed games (`--resume`)
- Game state persistence and resumption
- Player roles:
  - Villagers
  - Werewolves
  - Seer (special villager role)
  - Doctor (special villager role)
- Multi-threaded execution for parallel player actions
- Comprehensive logging system
- Apache 2.0 License
- README with setup instructions and usage examples
- Contributing guidelines
- Player avatar images for the viewer

### Documentation
- Link to research paper: [Werewolf Arena: A Framework for Evaluating LLM Social Reasoning](https://arxiv.org/abs/2407.13943)
- Setup instructions for Python environment
- Instructions for OpenAI API key configuration
- Instructions for GCP/Gemini setup
- Viewer usage guide

[Unreleased]: https://github.com/cajias/werewolf_arena/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cajias/werewolf_arena/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/cajias/werewolf_arena/releases/tag/v0.0.1
