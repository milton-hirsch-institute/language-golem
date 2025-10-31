<!-- Copyright 2025 The Milton Hirsch Institute, B.V.
     SPDX-License-Identifier: Apache-2.0
-->

# Style Guide

This document defines the coding and documentation standards for this project.

## Code Style

- Follow Google Python Style Guide
- Use Google-style docstrings for all functions, classes, and modules
- Code formatting enforced by `ruff format`
- Linting rules configured in `pyproject.toml`
- Markdown files should have 99 character column limit (except code blocks when necessary)
- Do not import symbols into modules. Always prefer to reference the module that the symbol
  is contained in.
  ```python
  # Correct
  from fakesd import waves
  result = waves.create_sawtooth_wave(...)

  # Incorrect
  from fakesd.waves import create_sawtooth_wave
  result = create_sawtooth_wave(...)
  ```

## Project Structure

The project follows standard Python package layout with `uv` as the build system. Dependencies
and project metadata are managed in `pyproject.toml`.

- Do not create `__init__.py` files in Python packages unless they are being used to as a way
to compose a single module interface from multiple sub-modules.

## Testing Standards

- Each class and top-level function should have a corresponding test class
- Methods and fixtures within a class should have their own test sub-class for organization
- Define test methods as static methods on test classes
- Simple functions with single test cases may use standalone test functions
- Modules with single class or function may be covered by top-level test functions
- Follow pytest conventions for test discovery and execution

## Commit Message Style

- Clear, concise subject line (50 characters or less)
- Blank line between subject and body
- Organize body into sections with bullet points (Changes, Features, Fixes, Tests, Refactoring)
- Only include relevant sections
- Do not end with generation attribution
