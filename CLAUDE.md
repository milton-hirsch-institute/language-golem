# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

## Project Type

Python library using `uv` for project management.

## License

This project is licensed under the Apache License 2.0.

## Development Commands

- `uv sync` - Install dependencies and sync environment
- `uv run pytest` - Run tests
- `uv run pytest tests/test_specific.py` - Run specific test file
- `uv run ruff check` - Lint code
- `uv run ruff format` - Format code
- `uv run mypy` - Type checking
- `uv build` - Build the package

## Code Style

- Follow Google Python Style Guide
- Use Google-style docstrings for all functions, classes, and modules
- Code formatting enforced by `ruff format`
- Linting rules configured in `pyproject.toml`
- Markdown files should have 99 character column limit (except code blocks when necessary)

## Project Structure

The project follows standard Python package layout with `uv` as the build system. Dependencies
and project metadata are managed in `pyproject.toml`.

## Commit Message Style

- Clear, concise subject line (50 characters or less)
- Blank line between subject and body
- Organize body into sections with bullet points (Changes, Features, Fixes, Tests, Refactoring)
- Only include relevant sections
- Do not end with generation attribution
