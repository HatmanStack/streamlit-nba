# Phase 1: [HYGIENIST] Cleanup

## Phase Goal

Remove dead code, unused exports, debug artifacts, and fix `.gitignore` to prevent future artifact commits. This is pure subtraction with no behavioral changes.

**Success criteria:** All 7 dead functions/classes identified in the health audit are removed. `.gitignore` covers all generated artifacts. No functional behavior changes. All existing tests still pass.

**Estimated tokens:** ~20k

## Prerequisites

- Phase 0 read and understood
- Repository cloned, `uv pip install -e ".[dev]"` completed
- Existing tests pass: `pytest`

## Tasks

### Task 1: Expand .gitignore

**Goal:** Prevent accidental commits of build artifacts, caches, coverage files, and binary model directories. Addresses health audit finding #2 (CRITICAL) and eval git-hygiene score 5/10.

**Files to Modify:**
- `.gitignore` - Rewrite with comprehensive patterns

**Prerequisites:** None

**Implementation Steps:**
- Replace the single-line `.gitignore` with a comprehensive Python `.gitignore`.
- Include patterns for: `__pycache__/`, `*.pyc`, `*.pyo`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `.venv/`, `venv/`, `uv.lock`, `winner_model/`, `debug_streamlit.py`, `*.keras` model files (if using download script) or keep `winner.keras` tracked (it is needed at runtime). Since the model is only 87KB and needed at runtime, keep it tracked but add `winner_model/` (the unused SavedModel directory).
- Do NOT add `snowflake_nba.csv`, `player_stats.txt`, or `schedule.txt` since these are runtime/training data needed by the app.

**Verification Checklist:**
- [x] `.gitignore` contains patterns for `__pycache__/`, `*.pyc`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `.venv/`, `venv/`, `winner_model/`
- [x] `git status` no longer shows `__pycache__/`, `.coverage`, `src/streamlit_nba.egg-info/` as untracked
- [x] `winner.keras` is NOT ignored (it is needed at runtime and only 87KB)

**Testing Instructions:** No tests needed. Visual verification via `git status`.

**Commit Message Template:**
```text
chore(gitignore): expand .gitignore to cover build artifacts and caches
```

---

### Task 2: Remove dead functions and classes from src/state/session.py

**Goal:** Remove 5 unused exports: `GameState` class, `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, `remove_player_from_team()`. Addresses health audit finding #4 (HIGH).

**Files to Modify:**
- `src/state/session.py` - Remove dead code
- `src/state/__init__.py` - Remove dead exports from `__all__`

**Prerequisites:** Task 1

**Implementation Steps:**
- Read `src/state/session.py` and `src/state/__init__.py` to understand current exports.
- Search the entire codebase for any usage of the 5 items to confirm they are truly unused. Search for: `GameState`, `get_home_team_names`, `set_difficulty`, `add_player_to_team`, `remove_player_from_team`.
- Remove the `GameState` dataclass (around lines 19-29).
- Remove the functions `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, `remove_player_from_team()` (around lines 86-163).
- Update `src/state/__init__.py` to remove these from `__all__` and from imports.
- Keep: `init_session_state()`, `get_away_stats()`, `get_home_team_df()`, and any other functions that ARE used.

**Verification Checklist:**
- [x] `GameState` class no longer exists in `session.py`
- [x] The 4 dead functions no longer exist in `session.py`
- [x] `src/state/__init__.py` exports only the functions that remain
- [x] `pytest` passes with no failures
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** Run existing test suite. No new tests needed since these functions had no tests.

**Commit Message Template:**
```text
refactor(dead-code): remove unused GameState and 4 dead functions from session.py
```

---

### Task 3: Remove dead functions from queries.py and html.py

**Goal:** Remove `get_player_by_full_name()` from queries and `safe_styled_text()` from html utils. Addresses health audit finding #5 (HIGH).

**Files to Modify:**
- `src/database/queries.py` - Remove `get_player_by_full_name()`
- `src/database/__init__.py` - Remove from exports
- `src/utils/html.py` - Remove `safe_styled_text()`
- `src/utils/__init__.py` - Remove from exports

**Prerequisites:** Task 1

**Implementation Steps:**
- Search codebase for `get_player_by_full_name` and `safe_styled_text` to confirm they are unused.
- Remove `get_player_by_full_name()` from `src/database/queries.py` (around lines 34-49).
- Remove `safe_styled_text()` from `src/utils/html.py` (around lines 73-108).
- Update both `__init__.py` files to remove these from `__all__` and imports.
- Check if any tests reference these functions. If tests exist for them, remove those test cases too.

**Verification Checklist:**
- [x] `get_player_by_full_name` does not appear in any source file
- [x] `safe_styled_text` does not appear in any source file
- [x] `__init__.py` exports updated
- [x] `pytest` passes
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** Run existing test suite. Remove any tests that test the deleted functions.

**Commit Message Template:**
```text
refactor(dead-code): remove unused get_player_by_full_name and safe_styled_text
```

---

### Task 4: Remove unused PlayerStats Pydantic model

**Goal:** Remove the `PlayerStats` model and `from_db_row()` factory that are never used in production code. Addresses eval architecture concern and health audit finding #12 (MEDIUM). Per ADR-3, we remove rather than integrate.

**Files to Modify:**
- `src/models/player.py` - Remove `PlayerStats` class and `from_db_row()`
- `src/models/__init__.py` - Remove `PlayerStats` from exports
- `tests/test_models.py` - Remove tests for `PlayerStats` (keep `DifficultySettings` tests)

**Prerequisites:** Task 1

**Implementation Steps:**
- Read `src/models/player.py` to identify `PlayerStats` class boundaries.
- Search for `PlayerStats` across the codebase to confirm it is only used in tests.
- Remove the `PlayerStats` class and `from_db_row()` method.
- Keep `DifficultySettings` and its validators since those are used by the app.
- Update `src/models/__init__.py` to remove `PlayerStats` from exports.
- Update `tests/test_models.py` to remove `PlayerStats` test cases. Keep `DifficultySettings` tests.
- Clean up any imports that are no longer needed after removing `PlayerStats` (e.g., `Any` if only used by `from_db_row`).

**Verification Checklist:**
- [x] `PlayerStats` class no longer exists
- [x] `from_db_row` no longer exists
- [x] `DifficultySettings` and its tests are untouched
- [x] `pytest` passes
- [x] `mypy src/` passes
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** Run full test suite. Verify `DifficultySettings` tests still pass.

**Commit Message Template:**
```text
refactor(dead-code): remove unused PlayerStats Pydantic model
```

---

### Task 5: Remove debug_streamlit.py reference from pyproject.toml

**Goal:** Remove the ruff per-file-ignores entry for `debug_streamlit.py` since the file is a local debug artifact, not committed code. Addresses doc audit structure issue #2.

**Files to Modify:**
- `pyproject.toml` - Remove `debug_streamlit.py` from `per-file-ignores`

**Prerequisites:** None

**Implementation Steps:**
- In `pyproject.toml`, find the `[tool.ruff.lint.per-file-ignores]` section.
- Remove the line `"debug_streamlit.py" = ["E402"]`.
- The `debug_streamlit.py` file itself is already in `.gitignore` (from Task 1) and untracked.

**Verification Checklist:**
- [x] `debug_streamlit.py` no longer appears in `pyproject.toml`
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** None needed.

**Commit Message Template:**
```text
chore(config): remove debug_streamlit.py from ruff per-file-ignores
```

---

### Task 6: Remove SQL injection validation (per ADR-4)

**Goal:** Remove the SQL injection regex and related code from `src/validation/inputs.py`. Keep character validation and length checks. Addresses health audit finding #11 (MEDIUM) and eval pragmatism concerns.

**Files to Modify:**
- `src/validation/inputs.py` - Remove SQL injection patterns and regex check
- `src/validation/__init__.py` - Update exports if needed
- `tests/test_validation.py` - Remove SQL injection test cases, keep character validation tests

**Prerequisites:** Task 1

**Implementation Steps:**
- Read `src/validation/inputs.py` to understand the full validation logic.
- Remove the `SQL_INJECTION_PATTERNS` compiled regex (around lines 8-24).
- In the validation function(s), remove the SQL injection pattern check.
- Keep: search term length validation, character allowlist checks, any `PlayerSearchInput` Pydantic model fields that are not SQL-related.
- Update `tests/test_validation.py`: remove parametrized SQL injection test vectors. Keep tests for character validation, length limits, and legitimate names like "O'Neal" and "J.R. Smith".
- Also remove the ruff ignore for `S608` (SQL injection false positive) from `pyproject.toml` since there will be no SQL-related code left.

**Verification Checklist:**
- [x] No SQL injection patterns or regex in `inputs.py`
- [x] Character validation and length checks still work
- [x] `pytest` passes (with updated test cases)
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** Run the validation tests specifically: `pytest tests/test_validation.py -v`

**Commit Message Template:**
```text
refactor(validation): remove SQL injection guards (no SQL database exists)
```

---

### Task 7: Remove finally:pass and fix duplicate on_page_load

**Goal:** Quick code hygiene fixes. Remove the no-op `finally: pass` block in `connection.py` and extract the duplicated `on_page_load()` pattern. Addresses health audit findings #16 (MEDIUM) and #18 (LOW).

**Files to Modify:**
- `src/database/connection.py` - Remove `finally: pass` block (around lines 72-73)
- `src/config.py` - Add a shared `configure_page()` function
- `pages/1_home_team.py` - Use shared function instead of local `on_page_load()`
- `pages/2_play_game.py` - Use shared function instead of local `on_page_load()`
- `app.py` - Use shared function instead of local `on_page_load()`

**Prerequisites:** None

**Implementation Steps:**
- In `src/database/connection.py`, find the `finally: pass` block in the context manager and remove it entirely (the `finally` keyword and the `pass` statement).
- In `src/config.py`, add a function `configure_page` that calls `st.set_page_config(layout="wide")`. This function will need to import streamlit, which is acceptable since it is a UI configuration function.
- In each of `app.py`, `pages/1_home_team.py`, and `pages/2_play_game.py`: remove the local `on_page_load()` function definition and its call. Replace with `from src.config import configure_page` and call `configure_page()`.

**Verification Checklist:**
- [x] No `finally: pass` in `connection.py`
- [x] `on_page_load` does not appear in any page file or `app.py`
- [x] `configure_page` exists in `src/config.py` and is called by all 3 entry points
- [x] `pytest` passes
- [x] `ruff check src/ tests/` passes

**Testing Instructions:** Run existing tests. The `configure_page` function is UI-only and does not need a unit test.

**Commit Message Template:**
```text
refactor(pages): extract shared configure_page, remove finally:pass
```

## Phase Verification

After completing all tasks in this phase:

1. Run `pytest` and confirm all tests pass.
2. Run `ruff check src/ tests/` and confirm no lint errors.
3. Run `mypy src/` and confirm no type errors.
4. Run `git diff --stat` and confirm only expected files changed.
5. Verify no dead code identified in the health audit remains.
