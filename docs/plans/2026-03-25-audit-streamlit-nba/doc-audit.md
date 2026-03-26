---
type: doc-health
docs_scanned: 2
code_modules_scanned: 8
findings:
  drift: 4
  gaps: 5
  stale: 0
  broken_links: 0
drift_prevention: markdownlint + lychee
language_stack: python + js/ts
---

> **Snapshot context:** This document captures pre-remediation findings from the 2026-03-25 audit. Items addressed during the remediation PR are annotated inline.

## DOCUMENTATION AUDIT

### SUMMARY
- Docs scanned: 2 files (README.md, CHANGELOG.md)
- Code modules scanned: 8 modules (app.py, 2 pages, 6 src packages, 1 script)
- Total findings: 4 drift, 5 gaps, 0 stale, 0 broken links, 1 config drift, 2 structure issues

---

### DRIFT (doc exists, doesn't match code)

1. **`README.md:3`** - Python version badge
   - Doc says: `python-3.11+-blue.svg` (badge shows "3.11+")
   - `pyproject.toml:6` says: `requires-python = ">=3.11"` (matches badge)
   - Runtime environment uses Python 3.13 (`.venv/lib/python3.13/`)
   - Badge is technically correct but worth noting the actual dev environment divergence.

2. **`README.md:19`** - "Multi-page Interface" feature description
   - Doc says: "Organized navigation between the home page, team builder, and game simulator."
   - Code has exactly two pages: `pages/1_home_team.py` (team builder) and `pages/2_play_game.py` (game/prediction). The main `app.py` is a simple landing page, not a "home page" in the navigational sense described. There is no distinct "game simulator" page separate from the predictor. The README implies three distinct pages; there are really two pages plus a landing.

3. **`README.md:37-50`** - Project structure tree
   - Doc shows `src/` with subdirectories only: `database/`, `ml/`, `models/`, `state/`, `utils/`, `validation/`
   - Code also has `src/config.py` and `src/__init__.py` at the `src/` level, which are not shown in the tree.
   - Tree does not mention `snowflake_nba.csv` (the actual data source used at runtime).
   - Tree does not mention `player_stats.txt` or `schedule.txt` (training data files).
   - Tree does not mention `winner_model/` directory (alternative SavedModel format alongside `winner.keras`).
   - Tree does not mention `.streamlit/config.toml`, `.devcontainer/devcontainer.json`, or `.github/` workflows (GitHub Actions CI).

4. **`README.md:21-22`** - "comprehensive database of historical NBA stats"
   - Doc says: "Search for players from a comprehensive database of historical NBA stats."
   - Code uses a single local CSV file (`snowflake_nba.csv`) loaded via pandas. The `connection.py` module is named `DatabaseConnectionError` and uses `get_connection()` as a context manager, but no actual database exists. The CHANGELOG v1.1.0 documents the transition from "remote database to local CSV-based data source" but the README still uses the word "database."

---

### GAPS (code exists, no doc)

1. **`src/config.py`** - Central configuration module with `PLAYER_COLUMNS`, `STAT_COLUMNS`, `TEAM_SIZE`, `MAX_QUERY_ATTEMPTS`, `DIFFICULTY_PRESETS`, score ranges, and `setup_logging()`. Not mentioned anywhere in documentation. *(Partially addressed: README now documents data file paths and config module.)*

2. **`src/models/player.py`** - ~~Pydantic models `PlayerStats` and `DifficultySettings` with validation logic.~~ *(Remediated: `PlayerStats` and `from_db_row` removed. Only `DifficultySettings` remains, which is an internal model used by session state.)*

3. **`src/state/session.py`** - ~~Session state management including `GameState` dataclass, `init_session_state()`, `get_away_stats()`, `get_home_team_df()`, `get_home_team_names()`, `set_difficulty()`, `add_player_to_team()`, `remove_player_from_team()`.~~ *(Remediated: `GameState`, `get_home_team_names`, `set_difficulty`, `add_player_to_team`, and `remove_player_from_team` removed. Remaining functions: `init_session_state()`, `get_away_stats()`, `get_home_team_df()`.)*

4. **`src/utils/html.py`** - ~~XSS protection utilities (`escape_html`, `safe_heading`, `safe_paragraph`, `safe_styled_text`).~~ *(Remediated: `safe_styled_text` removed. Remaining functions: `escape_html`, `safe_heading`, `safe_paragraph`.)*

5. **`src/validation/inputs.py`** - ~~SQL injection protection with `PlayerSearchInput` model, `SQL_INJECTION_PATTERNS`, `validate_search_term()`, `is_valid_search_term()`.~~ *(Remediated: `SQL_INJECTION_PATTERNS` regex removed. Validation now uses a character allowlist only. `PlayerSearchInput`, `validate_search_term()`, and `is_valid_search_term()` remain.)*

---

### STALE (doc exists, code doesn't)

None found. All documented features map to existing code.

---

### BROKEN LINKS

None found. The README contains one external link (`https://hatman-nba-fantasy-game.hf.space`) and external badge URLs. No internal relative links are used.

---

### STALE CODE EXAMPLES

1. **`README.md:64-66`** - Standard installation instructions
   - Doc says: `pip install -r requirements.txt`
   - The project has `pyproject.toml` with proper dependency declarations. The `requirements.txt` exists and works, but the README does not mention `pyproject.toml` or `uv pip install -e ".[dev]"` for dev setup. The "Quick Start with uv" section (lines 56-59) only shows `uv run streamlit run app.py` without explaining how to install dev dependencies with uv.

2. **`README.md:84-85`** - Linting command
   - Doc says: `ruff check .`
   - CI workflow (`ci.yml:31`) runs: `ruff check src/ tests/`
   - Minor inconsistency in scope (`.` vs `src/ tests/`), though both work.

---

### CONFIG DRIFT

1. **No `.env.example` or environment variable documentation exists.** The codebase reads no environment variables (confirmed via grep), so this is acceptable. However, the `snowflake_nba.csv` data file path is hardcoded in `src/database/connection.py:14` relative to the module location, and the `winner.keras` model path is hardcoded in `src/ml/model.py:13`. Neither path is documented or configurable.

2. **`README.md:96`** - Training script documentation
   - Doc says the script "performs an automated search for the best architecture and hyperparameters (optimizers, initializers, etc.) before saving the final `winner.keras` model."
   - The script (`scripts/compile_model.py:30-31`) requires `player_stats.txt` and `schedule.txt` as input data files. These files exist in the repo root but are not mentioned in the README or documented anywhere. A user following the README training instructions would not know these files are prerequisites.

---

### STRUCTURE ISSUES

1. **`winner_model/` directory undocumented** - A `winner_model/` directory exists at the project root containing a TensorFlow SavedModel format (`.pb` files). This appears to be an older or alternative model format alongside `winner.keras`. The code only references `winner.keras`. This directory is undocumented and may be a leftover artifact.

2. **`debug_streamlit.py` undocumented** - An untracked debug script exists at the project root. While it is not committed (per git status), it is listed in `pyproject.toml` ruff per-file-ignores (`debug_streamlit.py = ["E402"]`), suggesting it is a recognized development tool that should either be documented or removed from linter config.

3. **`docs/plans/` directory** - A `docs/plans/` directory exists but is not mentioned in the README project structure tree.
