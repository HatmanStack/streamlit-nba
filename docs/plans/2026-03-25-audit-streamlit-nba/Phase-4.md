# Phase 4: [FORTIFIER] Guardrails

## Phase Goal

Add CI hardening, pre-commit hooks, dependency consolidation, and type rigor improvements. These are additive guardrails that prevent regression.

**Success criteria:** Pre-commit hooks run ruff and mypy. Dependencies consolidated to `pyproject.toml` only. CI uses `uv`. Type annotations tightened (no unnecessary `Any`). Coverage enforcement in CI.

**Estimated tokens:** ~20k

## Prerequisites

- Phase 3 complete (tests passing at 70% coverage)
- All lint and type checks passing

## Tasks

### Task 1: Consolidate dependencies to pyproject.toml

**Goal:** Remove `requirements.txt` and `requirements-dev.txt` as duplicate dependency sources. Update CI to install from `pyproject.toml`. Addresses health audit finding #14 (MEDIUM) and ADR-5.

**Files to Modify:**
- `requirements.txt` - Delete this file
- `requirements-dev.txt` - Delete this file (after verifying its contents match `[project.optional-dependencies] dev`)
- `.github/workflows/ci.yml` - Update install step to use `pyproject.toml`

**Prerequisites:** None

**Implementation Steps:**
- Read `requirements-dev.txt` to verify it matches or is a subset of `pyproject.toml` `[project.optional-dependencies] dev`.
- Delete `requirements.txt`.
- Delete `requirements-dev.txt` (if it matches pyproject.toml dev deps; if it has extra deps, add them to pyproject.toml first).
- Update `.github/workflows/ci.yml`:
  - Replace `pip install -r requirements-dev.txt` with `pip install -e ".[dev]"`.
  - Optionally switch to `uv` in CI for faster installs:
    ```yaml
    - name: Install uv
      run: pip install uv
    - name: Install dependencies
      run: uv pip install -e ".[dev]" --system
    ```
- Update CI to add `--cov-fail-under=70` to the pytest command if not already there.

**Verification Checklist:**
- [x] `requirements.txt` deleted
- [x] `requirements-dev.txt` deleted
- [x] CI workflow installs from `pyproject.toml`
- [x] CI workflow still runs tests, ruff, and mypy successfully

**Testing Instructions:** Push to a branch and verify CI passes, or run the install and test commands locally.

**Commit Message Template:**
```text
ci(deps): consolidate to pyproject.toml, remove requirements files
```

---

### Task 2: Add pre-commit hooks

**Goal:** Add `.pre-commit-config.yaml` with ruff and mypy hooks to catch issues before commit. Addresses eval git-hygiene remediation target.

**Files to Modify:**
- `.pre-commit-config.yaml` - Create new file

**Prerequisites:** Task 1

**Implementation Steps:**
- Create `.pre-commit-config.yaml` at the project root with:
  ```yaml
  repos:
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.8.0  # Use latest stable version
      hooks:
        - id: ruff
          args: [--fix]
        - id: ruff-format
    - repo: https://github.com/pre-commit/mirrors-mypy
      rev: v1.13.0  # Use latest stable version
      hooks:
        - id: mypy
          additional_dependencies: [pandas-stubs]
          args: [--config-file=pyproject.toml]
          pass_filenames: false
          entry: mypy src/
  ```
- Add `pre-commit` to the dev dependencies in `pyproject.toml`:
  ```
  "pre-commit>=3.0.0",
  ```
- Verify the hooks work: `uvx pre-commit run --all-files`.
- Note: Use the latest stable versions of ruff and mypy that are compatible. Check PyPI for current versions.

**Verification Checklist:**
- [x] `.pre-commit-config.yaml` exists at project root
- [x] `pre-commit` is in dev dependencies
- [x] `uvx pre-commit run --all-files` passes

**Testing Instructions:** Run `uvx pre-commit run --all-files` and verify all hooks pass.

**Commit Message Template:**
```text
ci(hooks): add pre-commit config with ruff and mypy hooks
```

---

### Task 3: Tighten type annotations

**Goal:** Replace imprecise type annotations (`Any`, `tuple[Any, ...]`, `list[list]`) with specific types. Addresses eval type-rigor score of 7/10.

**Files to Modify:**
- `src/database/queries.py` - Fix return types
- `scripts/compile_model.py` - Fix type hints

**Prerequisites:** Phase 1 (dead code removed, so fewer files to fix)

**Implementation Steps:**
- In `src/database/queries.py`:
  - Find `tuple[Any, ...]` return types (around line 36) and replace with specific types. If the function returns player data columns, use a `TypedDict` or a specific tuple type like `tuple[str, str, float, ...]` matching the actual columns returned.
  - Find `list[tuple[str]]` return types (around line 14) and simplify to `list[str]` if the function returns a flat list of strings.
  - Remove `Any` import if no longer needed.
- In `scripts/compile_model.py`:
  - Change `list[list]` to `list[list[float]]` or more specific parameterized types (around line 85).
- Review `src/models/player.py` for any remaining `Any` imports that are no longer needed after `PlayerStats` removal.

**Verification Checklist:**
- [x] No `tuple[Any, ...]` in `queries.py`
- [x] No bare `list[list]` in `compile_model.py`
- [x] `mypy src/` passes
- [x] `pytest` passes

**Testing Instructions:** Run `mypy src/` and verify no new errors. Run existing tests.

**Commit Message Template:**
```text
refactor(types): tighten type annotations, remove unnecessary Any usage
```

---

### Task 4: Add coverage enforcement to CI

**Goal:** Ensure CI fails if coverage drops below the threshold. Addresses eval reproducibility concerns.

**Files to Modify:**
- `.github/workflows/ci.yml` - Add `--cov-fail-under=70` to pytest command

**Prerequisites:** Phase 3 Task 5 (coverage threshold set)

**Implementation Steps:**
- In `.github/workflows/ci.yml`, update the pytest command:
  ```yaml
  - name: Run tests
    run: pytest --cov=src --cov-report=term-missing --cov-fail-under=70
  ```
- This ensures CI fails if coverage drops, not just locally.

**Verification Checklist:**
- [x] CI pytest command includes `--cov-fail-under=70`

**Testing Instructions:** Verify the CI workflow file has the correct command.

**Commit Message Template:**
```text
ci(coverage): enforce 70% coverage threshold in CI
```

---

### Task 5: Clean up ruff ignores

**Goal:** Remove ruff ignore rules that are no longer relevant after Phase 1 cleanup. Addresses tech debt in linter config.

**Files to Modify:**
- `pyproject.toml` - Update ruff ignore list

**Prerequisites:** Phase 1 (SQL injection code removed), Phase 2 (error handling fixed)

**Implementation Steps:**
- Review the ruff `ignore` list in `pyproject.toml`:
  - `S608` (SQL injection false positive): Remove this. SQL injection code was deleted in Phase 1.
  - `S110` (try-except-pass): Review if still needed after the `finally: pass` removal. If no `except: pass` patterns remain, remove it.
  - Keep the other ignores that are still relevant (`S101`, `PLR0913`, `SIM105`, `PLR2004`, `S311`, `E501`).
- Run `ruff check src/ tests/` to verify no new violations surface.

**Verification Checklist:**
- [x] `S608` removed from ruff ignores (already removed in Phase 1)
- [x] `S110` removed if no longer needed
- [x] `ruff check src/ tests/` passes with the updated config

**Testing Instructions:** `ruff check src/ tests/`

**Commit Message Template:**
```text
chore(config): remove obsolete ruff ignore rules
```

## Phase Verification

1. Run `pytest --cov=src --cov-report=term-missing --cov-fail-under=70` and confirm pass.
2. Run `ruff check src/ tests/` with no errors.
3. Run `mypy src/` with no errors.
4. Run `uvx pre-commit run --all-files` and confirm all hooks pass.
5. Verify `requirements.txt` and `requirements-dev.txt` no longer exist.
6. Verify `.pre-commit-config.yaml` exists.
