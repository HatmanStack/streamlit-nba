# Project Roadmap

Items identified during the 2026-03-25 audit that were deferred, out of scope, or not examined. Organized by priority.

## High Priority

### Replace TensorFlow with a lightweight alternative
The neural network is 3 dense layers with 100 inputs. TensorFlow is ~2GB of installed dependency for something scikit-learn or ONNX Runtime can handle in a fraction of the size. This is the single biggest factor in cold start time and deployment package size.

- Retrain with scikit-learn (MLPClassifier) or export to ONNX/TFLite
- Update `src/ml/model.py`, `scripts/compile_model.py`, `pyproject.toml`
- Update `winner.keras` artifact and any model-loading tests
- Source: eval Problem-Solution Fit (6/10), health audit HIGH #6

### Run dependency vulnerability scan
`pip-audit` failed to run during the audit. Dependencies use open upper bounds (`>=`) which could pull vulnerable versions.

- Run `uvx pip-audit` and address findings
- Consider pinning upper bounds or using `uv.lock` for reproducibility
- Source: health audit automated scan (blocked)

### Migrate model files out of git history
`winner.keras` (87KB) and `winner_model/` (SavedModel format, unused) are tracked directly in git. As the model grows, this bloats repo history permanently.

- Remove `winner_model/` entirely (dead, never referenced in code)
- Move `winner.keras` to Git LFS or add a download script
- Source: health audit CRITICAL #2, Day 2 eval Git Hygiene (5/10)

## Medium Priority

### Make data and model paths configurable
`snowflake_nba.csv` path is hardcoded via `Path(__file__).resolve().parent.parent.parent` in `connection.py:14`. Model path is similarly hardcoded in `model.py:13`. Neither is configurable via environment variable.

- Add env var overrides (e.g., `NBA_DATA_PATH`, `NBA_MODEL_PATH`) with current paths as defaults
- Document in README under "Data Files and Configuration"
- Source: health audit LOW #20, doc audit CONFIG DRIFT #1

### Improve logging for serverless compatibility
`logging.basicConfig()` is called inside `configure_page()`, which runs at page load. This is better than the original module-import-time call, but still conflicts with Lambda/Cloud Functions runtimes that configure their own root logger.

- Use `logging.getLogger(__name__)` pattern without `basicConfig()` for library modules
- Only call `basicConfig()` in the Streamlit entry points, guarded by a check
- Source: health audit MEDIUM #17, stress eval Pragmatism (6/10)

### Add CONTRIBUTING.md
No contributing guide exists. Day 2 evaluation flagged this for onboarding.

- Branch strategy, PR process, how to run tests locally
- Reference the pre-commit hooks added in Phase 4
- Source: Day 2 eval Onboarding (7/10)

### Improve away team generation algorithm
The retry loop (up to 10 attempts) uses random sampling that can fail repeatedly with small pools. A pool-size pre-check before entering the loop would avoid futile iterations.

- Pre-check `len(pool) >= required` before sampling
- Consider stratified sampling for guaranteed one-pass results when pool is large enough
- Source: health audit MEDIUM #13, eval Creativity (6/10)

## Low Priority

### Page-level import-time execution
Streamlit pages execute business logic at module level during import. This is inherent to Streamlit's architecture and not fixable without abandoning the framework. Core modules (database, ML) were decoupled in the audit, but the pages themselves still run top-to-bottom on every rerun.

- Not actionable without a framework change
- If migrating to FastAPI or similar, this resolves naturally
- Source: health audit CRITICAL #3

### Add .env.example
The codebase currently reads no environment variables, so this is not urgent. If configurable paths are added (see above), create `.env.example` at that time.

- Source: Day 2 eval Onboarding (7/10)

## Not In Scope (Separate Initiatives)

### ML model quality evaluation
The audit examined code quality, not model quality. No assessment was made of prediction accuracy, training data freshness, or bias.

### Accessibility audit
No evaluation of the Streamlit UI for accessibility (screen readers, keyboard navigation, color contrast).

### Load and performance testing
No profiling of cold start time, memory footprint, or behavior under concurrent users. Relevant if deploying beyond the Hugging Face Space.
