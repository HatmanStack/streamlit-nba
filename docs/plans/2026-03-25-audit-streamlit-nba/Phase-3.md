# Phase 3: [IMPLEMENTER] Testing Improvements

## Phase Goal

Improve test coverage and test quality. Add integration tests for CSV data validation, tests for session state, and tests for HTML utilities. Raise the coverage threshold from 50% to 70%. Address the eval test-value score of 7/10.

**Success criteria:** Coverage threshold raised to 70% and CI passes at that threshold. New tests cover session state, HTML utilities, and CSV column validation. At least one test loads the real model file.

**Estimated tokens:** ~20k

## Prerequisites

- Phase 2 complete (Streamlit decoupled from src/, error handling fixed)
- All existing tests passing

## Tasks

### Task 1: Add integration test for CSV column validation

**Goal:** Verify that the actual `snowflake_nba.csv` column order matches `PLAYER_COLUMNS` in config. Addresses eval test-value remediation target.

**Files to Modify:**
- `tests/test_database.py` - Add integration test

**Prerequisites:** Phase 2 Task 1 (load_data decoupled from Streamlit)

**Implementation Steps:**
- Add a test function `test_csv_columns_match_config()` that:
  - Calls `load_data()` directly (no Streamlit mock needed after Phase 2).
  - Asserts that the DataFrame columns match `PLAYER_COLUMNS` from `src/config.py`.
  - Asserts the DataFrame is not empty.
- This test validates that the CSV data source and config are in sync, catching the kind of silent drift that `from_db_row` (now removed) was vulnerable to.

**Verification Checklist:**
- [x] Test loads real CSV and validates columns
- [x] Test passes
- [x] Test fails if a column is renamed in config (verify by temporarily changing a column name)

**Testing Instructions:** `pytest tests/test_database.py::test_csv_columns_match_config -v`

**Commit Message Template:**
```text
test(database): add integration test for CSV column validation
```

---

### Task 2: Add tests for session state management

**Goal:** Add tests for the remaining functions in `src/state/session.py`: `init_session_state()`, `get_away_stats()`, `get_home_team_df()`. Addresses health audit finding #21 (LOW).

**Files to Modify:**
- `tests/test_state.py` - Create new test file

**Prerequisites:** Phase 2 complete

**Implementation Steps:**
- Create `tests/test_state.py`.
- Mock `streamlit.session_state` as a plain dictionary for testing.
- Test `init_session_state()`:
  - Call the function with a mock session state.
  - Verify all expected keys are initialized.
  - Call it twice and verify it does not overwrite existing values.
- Test `get_away_stats()`:
  - Set up session state with known away team data.
  - Verify the function returns the expected stats.
- Test `get_home_team_df()`:
  - Set up session state with a known home team DataFrame.
  - Verify the function returns it correctly.
- Mock any `streamlit` imports at the module level using `unittest.mock.patch`.

**Verification Checklist:**
- [x] `tests/test_state.py` exists with at least 5 test functions
- [x] All tests pass
- [x] Tests do not require a Streamlit runtime

**Testing Instructions:** `pytest tests/test_state.py -v`

**Commit Message Template:**
```text
test(state): add tests for session state management functions
```

---

### Task 3: Add tests for HTML utility functions

**Goal:** Test the XSS escaping utilities in `src/utils/html.py`. Addresses health audit finding #21 (LOW) and doc audit gap #4.

**Files to Modify:**
- `tests/test_utils.py` - Create new test file

**Prerequisites:** None

**Implementation Steps:**
- Create `tests/test_utils.py`.
- Test `escape_html()`:
  - Verify it escapes `<`, `>`, `&`, `"`, `'` characters.
  - Verify it passes through safe strings unchanged.
- Test `safe_heading()`:
  - Verify it returns HTML with escaped content.
  - Verify XSS payloads like `<script>alert(1)</script>` are escaped in output.
- Test `safe_paragraph()`:
  - Similar to `safe_heading` tests.
- Do NOT test `safe_styled_text` since it was removed in Phase 1.

**Verification Checklist:**
- [x] `tests/test_utils.py` exists with tests for each exported function
- [x] XSS payloads are verified to be escaped
- [x] All tests pass

**Testing Instructions:** `pytest tests/test_utils.py -v`

**Commit Message Template:**
```text
test(utils): add tests for HTML escaping utilities
```

---

### Task 4: Add a real model loading test

**Goal:** Add at least one test in `test_ml.py` that loads the actual `winner.keras` model file to verify the model contract. Addresses eval test-value concern about over-mocking.

**Files to Modify:**
- `tests/test_ml.py` - Add integration test

**Prerequisites:** Phase 2 Task 2 (model decoupled from Streamlit)

**Implementation Steps:**
- Add a test function `test_load_real_model()` that:
  - Calls `get_winner_model()` (or the underlying load function) with the real `winner.keras` file.
  - Verifies the model is loaded successfully (not None).
  - Verifies the model has the expected input shape (100 features).
  - Verifies the model has the expected output shape (binary classification).
- Mark this test with `@pytest.mark.slow` or `@pytest.mark.integration` if desired, but it should run in CI since the model file is in the repo.
- Note: This test will require TensorFlow to be installed. It should work in CI since TensorFlow is a project dependency.

**Verification Checklist:**
- [x] Test loads real `winner.keras` file
- [x] Test verifies input/output shape
- [x] Test passes

**Testing Instructions:** `pytest tests/test_ml.py::TestLoadRealModel::test_load_real_model -v`

**Commit Message Template:**
```text
test(ml): add integration test with real model file
```

---

### Task 5: Raise coverage threshold to 70%

**Goal:** Increase the coverage `fail_under` threshold from 50% to 70%. Addresses eval git-hygiene remediation target.

**Files to Modify:**
- `pyproject.toml` - Change `fail_under = 50` to `fail_under = 70`

**Prerequisites:** Tasks 1-4 (new tests added to meet the threshold)

**Implementation Steps:**
- Run `pytest --cov=src --cov-report=term-missing` to check current coverage.
- If coverage is at or above 70%, update `pyproject.toml` line 113: change `fail_under = 50` to `fail_under = 70`.
- If coverage is below 70%, identify the uncovered modules and add targeted tests to reach the threshold before updating the config.

**Verification Checklist:**
- [x] `pyproject.toml` has `fail_under = 70`
- [x] `pytest --cov=src --cov-report=term-missing --cov-fail-under=70` passes

**Testing Instructions:** `pytest --cov=src --cov-report=term-missing --cov-fail-under=70`

**Commit Message Template:**
```text
test(coverage): raise coverage threshold from 50% to 70%
```

## Phase Verification

1. Run `pytest --cov=src --cov-report=term-missing --cov-fail-under=70` and confirm pass.
2. Verify new test files exist: `tests/test_state.py`, `tests/test_utils.py`.
3. Run `ruff check src/ tests/` with no errors.
4. Run `mypy src/` with no errors.
