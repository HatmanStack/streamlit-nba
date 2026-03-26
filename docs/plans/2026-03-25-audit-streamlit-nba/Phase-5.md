# Phase 5: [DOC-ENGINEER] Documentation Fixes

## Phase Goal

Fix all documentation drift, fill documentation gaps, and update the README to accurately reflect the current codebase state after all prior remediation phases.

**Success criteria:** README accurately describes the project structure, features, installation, and data sources. No documentation drift remains. Training script prerequisites documented.

**Estimated tokens:** ~15k

## Prerequisites

- Phases 1-4 complete (code changes finalized)
- All tests, lint, and type checks passing

## Tasks

### Task 1: Fix README feature descriptions and terminology

**Goal:** Correct the "Multi-page Interface" description and replace "database" language with "CSV data source." Addresses doc audit drift findings #2 and #4.

**Files to Modify:**
- `README.md` - Update feature descriptions

**Prerequisites:** None

**Implementation Steps:**
- Find the "Multi-page Interface" description (around line 19). Update to accurately describe the two pages plus landing: e.g., "Two-page Streamlit app with a team builder and game prediction simulator, plus a landing page."
- Find "comprehensive database of historical NBA stats" (around line 21-22). Replace "database" with "dataset" or "CSV data source." E.g., "Search for players from a dataset of historical NBA stats."
- Search the entire README for other uses of "database" that imply a live database connection. Update to reflect that data comes from a local CSV file.

**Verification Checklist:**
- [x] README does not describe three distinct pages
- [x] README does not use "database" to describe the CSV data source
- [x] Feature descriptions match actual app behavior

**Testing Instructions:** Read the README and verify accuracy against the app.

**Commit Message Template:**
```text
docs(readme): fix feature descriptions and data source terminology
```

---

### Task 2: Update README project structure tree

**Goal:** Make the project structure tree match the actual file layout after all remediation changes. Addresses doc audit drift finding #3.

**Files to Modify:**
- `README.md` - Update project structure section (around lines 37-50)

**Prerequisites:** Phases 1-4 complete

**Implementation Steps:**
- Update the project structure tree to include:
  - `src/config.py` and `src/__init__.py`
  - `snowflake_nba.csv` (the runtime data source)
  - `.github/workflows/` directory
  - `.pre-commit-config.yaml` (added in Phase 4)
  - `.streamlit/config.toml` (if it exists)
- Remove from the tree:
  - `requirements.txt` (deleted in Phase 4)
  - Any files that no longer exist after cleanup
- Do NOT include: `winner_model/` (gitignored), `debug_streamlit.py` (gitignored), `__pycache__/`, `.coverage`
- Keep the tree concise. Show top-level files and one level of `src/` subdirectories.

**Verification Checklist:**
- [x] Tree includes `src/config.py`
- [x] Tree includes `snowflake_nba.csv`
- [x] Tree does not list deleted files
- [x] Tree matches actual `ls` output

**Testing Instructions:** Run `ls -la` and compare with the documented tree.

**Commit Message Template:**
```text
docs(readme): update project structure tree to match codebase
```

---

### Task 3: Fix installation instructions

**Goal:** Update installation instructions to use `pyproject.toml` and `uv`. Remove references to deleted `requirements.txt`. Addresses doc audit stale code example #1.

**Files to Modify:**
- `README.md` - Update installation/quickstart section

**Prerequisites:** Phase 4 Task 1 (requirements files deleted)

**Implementation Steps:**
- Find the installation section (around lines 56-66).
- Replace `pip install -r requirements.txt` with `uv pip install -e ".[dev]"` for development setup, or `uv pip install -e .` for runtime only.
- Update the "Quick Start with uv" section to include dev dependency installation.
- Ensure the linting command matches CI: `ruff check src/ tests/` (not `ruff check .`). Addresses doc audit stale code example #2.

**Verification Checklist:**
- [x] No reference to `requirements.txt` in README
- [x] Installation uses `pyproject.toml` via `uv pip install`
- [x] Lint command matches CI workflow

**Testing Instructions:** Follow the installation instructions on a clean checkout and verify they work.

**Commit Message Template:**
```text
docs(readme): update installation to use pyproject.toml and uv
```

---

### Task 4: Document training script prerequisites

**Goal:** Document that `player_stats.txt` and `schedule.txt` are required by the training script. Addresses doc audit config drift #2.

**Files to Modify:**
- `README.md` - Update training script section (around line 96)

**Prerequisites:** None

**Implementation Steps:**
- Find the training script documentation section.
- Add a note that `player_stats.txt` and `schedule.txt` must exist in the project root for the training script to work.
- Mention that `winner.keras` is the output of the training script and is required at runtime.

**Verification Checklist:**
- [x] Training script prerequisites listed
- [x] `player_stats.txt` and `schedule.txt` mentioned as inputs
- [x] `winner.keras` mentioned as output

**Testing Instructions:** Read the section and verify it matches `scripts/compile_model.py` input file paths.

**Commit Message Template:**
```text
docs(readme): document training script prerequisites
```

---

### Task 5: Add data file and model path documentation

**Goal:** Document the hardcoded paths for data files and model files so developers know what to change if the project structure changes. Addresses doc audit config drift #1 and health audit finding #20 (LOW).

**Files to Modify:**
- `README.md` - Add a "Data Files" or "Configuration" section

**Prerequisites:** None

**Implementation Steps:**
- Add a brief section to the README (or expand the existing architecture section) that describes:
  - `snowflake_nba.csv`: loaded by `src/database/connection.py`, path resolved relative to the module location.
  - `winner.keras`: loaded by `src/ml/model.py`, path resolved relative to the module location.
  - `src/config.py`: central configuration for column names, team size, difficulty presets, and logging.
- Keep it concise. Two or three sentences per file.

**Verification Checklist:**
- [x] Data file paths documented
- [x] Model file path documented
- [x] Config module mentioned

**Testing Instructions:** Read the section for accuracy.

**Commit Message Template:**
```text
docs(readme): document data file paths and configuration
```

## Phase Verification

1. Read the entire README and verify every claim matches the current codebase.
2. Verify the project structure tree matches `ls` output.
3. Verify installation instructions work from scratch.
4. Run `ruff check src/ tests/` (the README-documented command) and confirm it works.
5. No documentation drift findings remain from the doc audit.
