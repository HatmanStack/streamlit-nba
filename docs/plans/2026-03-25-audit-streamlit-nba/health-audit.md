---
type: repo-health
overall_health: FAIR
findings:
  critical: 3
  high: 6
  medium: 8
  low: 5
---

## CODEBASE HEALTH AUDIT

### EXECUTIVE SUMMARY
- **Overall health:** FAIR
- **Biggest structural risk:** Streamlit framework (`st.cache_resource`, `st.cache_data`) is coupled directly into business logic modules (ML model, database connection), making the core logic untestable and undeployable outside of Streamlit.
- **Biggest operational risk:** Binary model file (87KB `.keras`) and large data files (394K CSV, 128K schedule.txt, 21K player_stats.txt) are committed directly to git, and the `.gitignore` is nearly empty (only `/venv`).
- **Total findings:** 3 critical, 6 high, 8 medium, 5 low

---

### TECH DEBT LEDGER

#### CRITICAL

1. **[Architectural Debt]** `src/ml/model.py:7-22` and `src/database/connection.py:9,29`
   - **The Debt:** Core business modules (`ml.model` and `database.connection`) directly import and use `streamlit` (`st.cache_resource`, `st.cache_data`). The ML model loader uses `@st.cache_resource` (line 22) and the data loader uses `@st.cache_data` (line 29). This means these modules cannot be imported or tested without a Streamlit runtime. For a serverless deployment target, this is a fundamental blocker: Lambda/Cloud Functions cannot run the Streamlit caching layer.
   - **The Risk:** The application is permanently locked to the Streamlit runtime. Any attempt to reuse the prediction logic in a Lambda handler, CLI tool, or API endpoint will fail at import time. Testing requires mocking Streamlit internals.

2. **[Operational Debt]** `.gitignore:1` (entire file is just `/venv`)
   - **The Debt:** The `.gitignore` is a single line: `/venv`. The repository tracks binary files (`winner.keras` at 87KB, `winner_model/` directory with SavedModel protobuf files), large data files (`snowflake_nba.csv` at 394KB, `schedule.txt` at 128KB, `player_stats.txt` at 21KB), a `.coverage` file (68KB), `__pycache__/` directories, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, a second `.venv/` directory, `uv.lock`, `debug_streamlit.py`, and `src/streamlit_nba.egg-info/`. Git status shows these are untracked but only because they were never added; the `.gitignore` does not prevent future accidental commits.
   - **The Risk:** Binary and generated artifacts bloat the repository. The `.coverage` file, `__pycache__` directories, and cache directories are transient build artifacts. The `winner.keras` and `winner_model/` are tracked model binaries that will accumulate in git history. For serverless cold starts, pulling a bloated deployment package increases init time.

3. **[Architectural Debt]** `pages/1_home_team.py:1-161` and `pages/2_play_game.py:1-206`
   - **The Debt:** Page modules execute business logic at module level (outside functions) during import. `1_home_team.py` calls `on_page_load()`, `init_session_state()`, `find_player()`, `find_home_team()`, and renders UI at lines 13, 27, 30, 32-42, 103-104, 127-161. `2_play_game.py` does the same at lines 36, 39, 42-43, 114-198. There is no separation between the controller logic and the view. All database queries, ML predictions, and UI rendering happen in a single top-to-bottom script execution.
   - **The Risk:** No unit of this code can be tested in isolation. Any import of a page module triggers the entire page flow. Serverless deployment is incompatible with this pattern since there is no request handler to invoke.

#### HIGH

4. **[Structural Debt]** `src/state/session.py:19-29`, `src/state/session.py:86-163`
   - **The Debt:** Five exported functions/classes in `session.py` are never used anywhere in the codebase: `GameState` (defined but unused), `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, and `remove_player_from_team()`. They are exported via `src/state/__init__.py` but never imported by any page or test.
   - **The Risk:** Dead code that increases maintenance surface. `GameState` duplicates the dict-based state in `init_session_state()`, creating confusion about which pattern is canonical.

5. **[Structural Debt]** `src/database/queries.py:34-49` and `src/utils/html.py:73-108`
   - **The Debt:** `get_player_by_full_name()` is defined and exported via `__init__.py` but never called by any page, test, or script. `safe_styled_text()` is defined but never called anywhere in the codebase.
   - **The Risk:** Dead code with no test coverage, adding maintenance burden.

6. **[Operational Debt]** `src/ml/model.py:44-45`
   - **The Debt:** `load_model()` (TensorFlow Keras) is called with no timeout and no size/memory guard. TensorFlow model loading is a heavyweight operation that loads the entire model into memory. For a serverless target (Lambda has 512MB-10GB memory, 15-minute timeout), loading a Keras model with the full TensorFlow runtime is a cold start performance concern.
   - **The Risk:** TensorFlow is one of the largest Python packages (>500MB installed). Cold start on Lambda with TensorFlow can exceed 10 seconds. There is no fallback, no lightweight model format (like ONNX or TFLite), and no lazy loading strategy.

7. **[Code Hygiene Debt]** `src/database/connection.py:48`, `src/database/connection.py:69`
   - **The Debt:** Broad `except Exception` catch blocks that re-raise as custom exceptions. At `connection.py:48`, any exception from `pd.read_csv()` is caught and wrapped. At `connection.py:69`, any exception from data access is caught and wrapped. While re-raising is better than swallowing, catching the base `Exception` can mask programming errors (e.g., `TypeError`, `KeyError`).
   - **The Risk:** Bugs in data processing code could be silently wrapped as `DatabaseConnectionError`, making debugging harder. The broad catch at line 69 includes the `finally: pass` block (line 72-73), which is a no-op.

8. **[Architectural Debt]** `pages/1_home_team.py:66` and `pages/1_home_team.py:87-88`
   - **The Debt:** f-string interpolation in logging calls: `logger.error(f"Database connection error: {e}")`. This evaluates the f-string even when the log level is above ERROR. Appears at 6 locations in `1_home_team.py` and 4 locations in `2_play_game.py`.
   - **The Risk:** Minor performance overhead on every request. In a high-throughput serverless context, unnecessary string formatting adds up.

9. **[Operational Debt]** `src/ml/model.py:83-114`
   - **The Debt:** `analyze_team_stats()` accepts `list[list[float]]` but performs no validation on the inner list lengths or the number of players. If a team has fewer or more than 5 players with 10 stats each, the reshape at lines 110-112 will silently produce arrays of unexpected shape. The only shape check is in `predict_winner()` at line 69, which checks for `(1, 100)` after the damage is done.
   - **The Risk:** Silent data corruption. If `STAT_COLUMNS` is modified or player count differs, the model receives garbage input without any clear error message. The error would surface as a generic `ValueError` from numpy reshape.

#### MEDIUM

10. **[Code Hygiene Debt]** `debug_streamlit.py:1-63`
    - **The Debt:** Debug script committed to the repository with print statements, mock Streamlit setup, and simulation logic. Not in `.gitignore`, not in any test suite.
    - **The Risk:** Confusion about whether this is a supported tool or leftover artifact. Contains hardcoded player names.

11. **[Structural Debt]** `src/validation/inputs.py:8-28`
    - **The Debt:** Elaborate SQL injection detection regex for a codebase that uses pandas DataFrames, not SQL databases. The data layer reads from a local CSV via pandas. There are no SQL queries anywhere in the application.
    - **The Risk:** False sense of security and unnecessary complexity. Solves a problem that does not exist in this architecture.

12. **[Structural Debt]** `src/models/player.py:10-81`
    - **The Debt:** Full Pydantic model `PlayerStats` with 27 fields and a `from_db_row()` factory method. Neither the model nor the factory method is used anywhere outside tests. The application works entirely with raw pandas DataFrames.
    - **The Risk:** Maintained model definition with no runtime usage. Changes to the DataFrame schema must be synchronized in two places (the Pydantic model and `PLAYER_COLUMNS` in config), but only the config is actually used.

13. **[Operational Debt]** `src/database/queries.py:102-147`
    - **The Debt:** The retry loop (up to `MAX_QUERY_ATTEMPTS = 10`) uses random sampling that can fail repeatedly if pool sizes are marginal. Each iteration creates new DataFrame slices. There is no exponential backoff or pool-size pre-check to fast-fail.
    - **The Risk:** On a serverless target with execution time limits, 10 retries of DataFrame operations with small pools waste compute.

14. **[Architectural Debt]** `requirements.txt:1-5` vs `pyproject.toml:7-13`
    - **The Debt:** Dependencies are declared in both `requirements.txt` and `pyproject.toml` with identical content. Dual source of truth.
    - **The Risk:** Dependency drift when one file is updated but not the other.

15. **[Operational Debt]** `pages/2_play_game.py:128-129`
    - **The Debt:** Away team is only generated when `st.session_state.get("away_team_df") is None or st.session_state.away_team_df.empty`. If data generation fails silently (returns empty DataFrame), the code does not clear the cached empty DataFrame, so subsequent reruns will not retry.
    - **The Risk:** One-time failure permanently prevents game play until the user clicks "Play New Team" manually.

16. **[Code Hygiene Debt]** `src/database/connection.py:72-73`
    - **The Debt:** `finally: pass` block in the context manager does nothing.
    - **The Risk:** Vestigial code that suggests cleanup was intended but never implemented.

17. **[Structural Debt]** `src/config.py:73-93`
    - **The Debt:** `setup_logging()` is called at module level (line 93), meaning logging is configured the moment any module imports `config.py`. It calls `logging.basicConfig()` which sets the root logger.
    - **The Risk:** In a serverless environment, the Lambda runtime configures its own root logger. Calling `basicConfig()` at import time can conflict with the runtime's logging setup.

#### LOW

18. **[Code Hygiene Debt]** `pages/1_home_team.py:22-27`, `pages/2_play_game.py:31-36`, `app.py:8-13`
    - **The Debt:** `on_page_load()` function defined and immediately called in three separate files, each containing only `st.set_page_config(layout="wide")`. Identical one-liner duplicated three times.
    - **The Risk:** Minor duplication. If page config needs to change, three files must be updated.

19. **[Code Hygiene Debt]** `src/models/player.py:95-104` and `src/models/player.py:119-123`
    - **The Debt:** Duplicate validation logic in `DifficultySettings`. The `validate_preset_name` field validator (line 95) checks if the name is valid, and `from_preset()` (line 119) performs the same check again before calling the constructor.
    - **The Risk:** Redundant code path. The error message format differs slightly between the two checks.

20. **[Code Hygiene Debt]** `src/database/connection.py:14`
    - **The Debt:** CSV path is resolved via `Path(__file__).resolve().parent.parent.parent / "snowflake_nba.csv"`, hardcoding a relative traversal depth. Not configurable via environment variable or config.
    - **The Risk:** Fragile path resolution. If the module is moved or the project structure changes, the path breaks silently.

21. **[Structural Debt]** No tests for `src/state/session.py` or page modules
    - **The Debt:** The test suite covers `models`, `validation`, `ml`, and `database` but has no tests for session state management or any page-level integration tests.
    - **The Risk:** Coverage threshold is set at 50%, which is low for production code.

22. **[Code Hygiene Debt]** `winner_model/` directory tracked alongside `winner.keras`
    - **The Debt:** Two copies of the trained model exist in the repository: `winner.keras` (87KB, Keras native format) and `winner_model/` (SavedModel format with protobuf files). Only `winner.keras` is referenced in code.
    - **The Risk:** `winner_model/` is dead weight in the repository, never referenced by any code.

---

### QUICK WINS

1. `/.gitignore` -- Expand to cover `__pycache__/`, `*.pyc`, `.coverage`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `.venv/`, `uv.lock`, `debug_streamlit.py`, `winner_model/` (estimated effort: < 15 minutes)

2. `src/database/connection.py:72-73` -- Remove the `finally: pass` no-op block (estimated effort: < 5 minutes)

3. `src/state/session.py:19-29`, `src/state/session.py:86-163` -- Remove unused `GameState` class, `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, and `remove_player_from_team()` functions (estimated effort: < 30 minutes)

4. `src/utils/html.py:73-108` and `src/database/queries.py:34-49` -- Remove dead functions `safe_styled_text()` and `get_player_by_full_name()`, update `__init__.py` exports (estimated effort: < 30 minutes)

5. `pages/*.py` and `app.py` -- Extract duplicated `on_page_load()` into `src/config.py` or a shared module (estimated effort: < 30 minutes)

---

### AUTOMATED SCAN RESULTS

- **Dead code:** Manual analysis identified 7 unused functions/classes: `GameState`, `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, `remove_player_from_team()`, `get_player_by_full_name()`, `safe_styled_text()`
- **Vulnerability scan:** Unable to run `pip-audit`. Note: dependency pins use open upper bounds (`>=`) which could pull vulnerable versions
- **Secrets scan:** No hardcoded secrets, API keys, or high-entropy strings found in source files. No `.env` files present.
- **Git hygiene:** `.gitignore` covers only `/venv`. Binary files (`winner.keras`, `winner_model/`) and data files (`snowflake_nba.csv`, `player_stats.txt`, `schedule.txt`) are tracked in git. Generated artifacts (`.coverage`, `__pycache__/`, cache directories) are untracked but unprotected.
- **Type safety:** No `# type: ignore` comments found. Mypy strict mode enabled. Third-party libraries have `ignore_missing_imports = true` (appropriate).
- **Debug artifacts:** No `print()`, `TODO`, `FIXME`, or `debugger` statements in `src/`. `debug_streamlit.py` in repo root contains print statements.
