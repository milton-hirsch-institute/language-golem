<!-- Copyright 2025 The Milton Hirsch Institute, B.V.
     SPDX-License-Identifier: Apache-2.0
-->

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

## Style Guide

See [STYLE.md](STYLE.md) for coding standards, testing conventions, and commit message format.
