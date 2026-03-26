# Phase 2: [IMPLEMENTER] Architecture and Code Fixes

## Phase Goal

Fix structural and architectural issues: decouple Streamlit caching from business logic, fix error handling, improve input validation, add data shape guards, and fix logging. This phase addresses the critical architectural debt and high-severity findings.

**Success criteria:** `src/` modules can be imported and tested without a Streamlit runtime. Error handling uses specific exceptions. Logging uses lazy formatting. Input validation on ML pipeline prevents silent shape errors.

**Estimated tokens:** ~30k

## Prerequisites

- Phase 1 complete (dead code removed, clean baseline)
- All tests passing

## Tasks

### Task 1: Decouple Streamlit caching from src/database/connection.py

**Goal:** Remove `@st.cache_data` from `load_data()` so that `src/database/connection.py` can be imported without Streamlit. Move caching to the page layer. Addresses health audit finding #1 (CRITICAL).

**Files to Modify:**
- `src/database/connection.py` - Remove `import streamlit as st` and `@st.cache_data` decorator
- `pages/1_home_team.py` - Cache the data load call at the page level
- `pages/2_play_game.py` - Cache the data load call at the page level

**Prerequisites:** None

**Implementation Steps:**
- In `src/database/connection.py`:
  - Remove `import streamlit as st`.
  - Remove the `@st.cache_data` decorator from `load_data()`. The function itself stays unchanged; it still reads the CSV and returns a DataFrame.
  - The `get_connection()` context manager should also be simplified. Per the eval audit, it wraps a cached DataFrame read with no actual resource cleanup. Simplify: make `get_connection()` a plain function that calls `load_data()` and returns the DataFrame directly, OR keep the context manager but remove the ceremony. Recommended: replace with a plain function `get_data()` that returns `load_data()`.
- In the page files (`pages/1_home_team.py`, `pages/2_play_game.py`), wherever `get_connection()` or `load_data()` is called:
  - Add `@st.cache_data` to a local wrapper function if caching is needed, OR use `st.cache_data` inline.
  - The simplest approach: create a module-level cached wrapper in each page file:
    ```python
    @st.cache_data
    def _load_nba_data() -> pd.DataFrame:
        return load_data()
    ```
  - Replace `get_connection()` context manager usage with direct calls to `_load_nba_data()`.

**Verification Checklist:**
- [x] `src/database/connection.py` does not import `streamlit`
- [x] `python -c "from src.database.connection import load_data"` succeeds without Streamlit installed (or mocked)
- [x] Pages still load data correctly (manual test with `streamlit run app.py` if possible)
- [x] `pytest` passes
- [x] `mypy src/` passes

**Testing Instructions:**
- Update `tests/test_database.py` to remove any Streamlit mocking for `connection.py`.
- Add a simple test that calls `load_data()` directly and verifies it returns a DataFrame with expected columns.

**Commit Message Template:**
```text
refactor(database): decouple Streamlit caching from connection module
```

---

### Task 2: Decouple Streamlit caching from src/ml/model.py

**Goal:** Remove `@st.cache_resource` from the model loading function so `src/ml/model.py` can be imported without Streamlit. Addresses health audit finding #1 (CRITICAL).

**Files to Modify:**
- `src/ml/model.py` - Remove `import streamlit as st` and `@st.cache_resource`
- `pages/2_play_game.py` - Cache model loading at the page level

**Prerequisites:** Task 1

**Implementation Steps:**
- In `src/ml/model.py`:
  - Remove `import streamlit as st`.
  - Remove `@st.cache_resource` decorator from the model loading function (around line 22).
  - The function itself stays the same: it loads and returns the Keras model.
- In `pages/2_play_game.py`:
  - Add a cached wrapper for model loading:
    ```python
    @st.cache_resource
    def _get_model():
        return get_winner_model()
    ```
  - Replace direct calls to `get_winner_model()` with `_get_model()`.

**Verification Checklist:**
- [x] `src/ml/model.py` does not import `streamlit`
- [x] `python -c "from src.ml.model import get_winner_model"` succeeds without Streamlit
- [x] `pytest` passes
- [x] `mypy src/` passes

**Testing Instructions:**
- Update `tests/test_ml.py` to remove any Streamlit mocking that was needed due to the `st.cache_resource` import.

**Commit Message Template:**
```text
refactor(ml): decouple Streamlit caching from model module
```

---

### Task 3: Fix error handling - narrow exception catches

**Goal:** Replace broad `except Exception` catches with specific exception types. Remove duplicate logging. Addresses health audit finding #7 (HIGH).

**Files to Modify:**
- `src/database/connection.py` - Narrow exception catches at lines ~48 and ~69

**Prerequisites:** Task 1

**Implementation Steps:**
- At `connection.py` around line 48 (the `pd.read_csv()` call):
  - Replace `except Exception as e` with specific exceptions: `except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError) as e`.
  - Keep the re-raise as `DatabaseConnectionError`.
- At `connection.py` around line 69 (data access):
  - Replace `except Exception as e` with the specific exceptions that could actually occur (e.g., `KeyError`, `ValueError`).
  - Keep the re-raise as the appropriate custom exception.
- Review callers in pages to ensure they catch the custom exceptions, not bare `Exception`.

**Verification Checklist:**
- [x] No `except Exception` in `connection.py`
- [x] All exception catches use specific types
- [x] `pytest` passes
- [x] `mypy src/` passes

**Testing Instructions:**
- Existing tests should cover this. Add a test that verifies a `FileNotFoundError` is raised as `DatabaseConnectionError`.

**Commit Message Template:**
```text
fix(database): narrow exception catches to specific types
```

---

### Task 4: Fix logging - replace f-strings with lazy formatting

**Goal:** Replace f-string interpolation in logging calls with `%s` lazy formatting. Addresses health audit finding #8 (HIGH).

**Files to Modify:**
- `pages/1_home_team.py` - Fix ~6 logging calls
- `pages/2_play_game.py` - Fix ~4 logging calls
- `src/database/connection.py` - Fix any f-string logging calls

**Prerequisites:** None

**Implementation Steps:**
- Search all Python files for patterns like `logger.error(f"` or `logger.warning(f"` or `logger.info(f"`.
- Replace each with lazy formatting:
  ```python
  # Before
  logger.error(f"Database connection error: {e}")
  # After
  logger.error("Database connection error: %s", e)
  ```
- Apply this change consistently across all files.

**Verification Checklist:**
- [x] No f-strings in any `logger.*()` calls
- [x] `ruff check src/ tests/` passes
- [x] `pytest` passes

**Testing Instructions:** No new tests needed. This is a mechanical replacement.

**Commit Message Template:**
```text
fix(logging): replace f-string logging with lazy %s formatting
```

---

### Task 5: Add input shape validation to ML pipeline

**Goal:** Add explicit validation of player stat array shapes before model prediction. Addresses health audit finding #9 (HIGH).

**Files to Modify:**
- `src/ml/model.py` - Add validation in `analyze_team_stats()`
- `src/config.py` - Verify `TEAM_SIZE` and `STAT_COLUMNS` constants are defined

**Prerequisites:** Task 2

**Implementation Steps:**
- In `analyze_team_stats()` (around lines 83-114):
  - Before processing, validate that the input list has exactly `TEAM_SIZE` (5) players.
  - Validate that each player's stat list has exactly `len(STAT_COLUMNS)` (10) elements.
  - Raise a `ValueError` with a descriptive message if validation fails, e.g.: `f"Expected {TEAM_SIZE} players, got {len(stats)}"` and `f"Player {i} has {len(player_stats)} stats, expected {len(STAT_COLUMNS)}"`.
- Import `TEAM_SIZE` and `STAT_COLUMNS` (or their lengths) from `src/config.py`.

**Verification Checklist:**
- [x] `analyze_team_stats` raises `ValueError` if player count != 5
- [x] `analyze_team_stats` raises `ValueError` if any player has wrong stat count
- [x] Existing tests pass
- [x] New tests cover the validation

**Testing Instructions:**
- Add tests in `tests/test_ml.py`:
  - Test with wrong number of players (4 and 6), expect `ValueError`.
  - Test with a player having wrong number of stats (9 instead of 10), expect `ValueError`.

**Commit Message Template:**
```text
fix(ml): add input shape validation before model prediction
```

---

### Task 6: Fix DifficultySettings duplicate validation

**Goal:** Remove redundant validation in `DifficultySettings`. Addresses health audit finding #19 (LOW).

**Files to Modify:**
- `src/models/player.py` - Remove duplicate validation in either `validate_preset_name` or `from_preset()`

**Prerequisites:** Phase 1 Task 4 (PlayerStats removal)

**Implementation Steps:**
- Read the current state of `src/models/player.py` after Phase 1 cleanup.
- The `validate_preset_name` field validator (around line 95) checks if name is valid.
- The `from_preset()` class method (around line 119) performs the same check again.
- Remove the redundant check from `from_preset()` since the Pydantic validator will catch it during construction. Let `from_preset()` simply construct the instance and trust Pydantic validation.

**Verification Checklist:**
- [x] Only one validation path for preset names
- [x] `pytest tests/test_models.py` passes
- [x] Invalid preset names still raise appropriate errors

**Testing Instructions:** Existing `DifficultySettings` tests should cover this. Verify they pass.

**Commit Message Template:**
```text
fix(models): remove duplicate validation in DifficultySettings
```

---

### Task 7: Fix compile_model.py create_stats mutation

**Goal:** Fix the `create_stats` function to use slicing instead of destructive `del` operations. Addresses eval creativity concern.

**Files to Modify:**
- `scripts/compile_model.py` - Fix `create_stats()` (around lines 73-113)

**Prerequisites:** None

**Implementation Steps:**
- Read `scripts/compile_model.py` to understand `create_stats()`.
- Replace `del home_stats[i][j][0]` patterns with slicing: use `row[1:]` to skip the first element instead of deleting it.
- The function should produce the same output without mutating its input lists.
- Fix type hints: change `list[list]` to `list[list[float]]` or more precise types.

**Verification Checklist:**
- [x] No `del` operations on input data in `create_stats`
- [x] `ruff check scripts/` passes
- [x] Function produces same output (manual verification or add a simple test)

**Testing Instructions:** This is a training script, not part of the test suite. Manual verification that the output is unchanged, or add a simple test comparing old behavior vs new.

**Commit Message Template:**
```text
fix(scripts): replace destructive del with slicing in create_stats
```

---

### Task 8: Fix module-level logging setup

**Goal:** Move `setup_logging()` call from module-level to an explicit initialization point. Addresses health audit finding #17 (MEDIUM).

**Files to Modify:**
- `src/config.py` - Remove module-level `setup_logging()` call (line 93)
- `app.py` - Call `setup_logging()` explicitly
- `pages/1_home_team.py` - Call `setup_logging()` if not already initialized
- `pages/2_play_game.py` - Call `setup_logging()` if not already initialized

**Prerequisites:** Task 7 (Phase 1, the configure_page extraction)

**Implementation Steps:**
- In `src/config.py`, remove the `setup_logging()` call at module level (line 93). Keep the function definition.
- In the `configure_page()` function (added in Phase 1), add a call to `setup_logging()` so logging is configured when the page is set up. This centralizes both page config and logging init.
- Alternatively, call `setup_logging()` in each entry point (`app.py`, page files) right after `configure_page()`.

**Verification Checklist:**
- [x] `setup_logging()` is NOT called at module level in `config.py`
- [x] `setup_logging()` IS called in each entry point
- [x] `pytest` passes
- [x] Logging still works when running the app

**Testing Instructions:** Run existing tests. The module-level call removal should not break tests since tests typically configure their own logging.

**Commit Message Template:**
```text
fix(config): move logging setup from module-level to explicit init
```

## Phase Verification

1. Run `pytest --cov=src --cov-report=term-missing` and confirm all tests pass.
2. Run `ruff check src/ tests/` with no errors.
3. Run `mypy src/` with no errors.
4. Verify: `python -c "from src.database.connection import load_data; from src.ml.model import get_winner_model"` succeeds without importing Streamlit (the imports should not trigger `import streamlit`).
5. No `except Exception` in `src/database/connection.py`.
6. No f-string logging in any `logger.*()` call.
