# Phase 0: Foundation

This phase defines shared conventions, architecture decisions, and testing strategy that apply to all subsequent phases.

## Architecture Decisions

### ADR-1: Keep Streamlit as the runtime, but decouple caching from business logic

The app is a Streamlit project and will remain one. The audit flags `@st.cache_resource` and `@st.cache_data` decorators embedded in `src/ml/model.py` and `src/database/connection.py`. The fix is to move caching decorators to the Streamlit layer (pages/app) and keep `src/` modules as plain Python. This allows `src/` to be imported and tested without a Streamlit runtime.

### ADR-2: Keep TensorFlow for now; do not swap ML framework in this remediation

Swapping TensorFlow for scikit-learn or ONNX is a significant change that affects the training script, model file, and prediction pipeline. The eval audit suggests it but classifies it as MEDIUM complexity. This remediation focuses on structural quality, not framework migration. A follow-up plan can address the TF dependency.

### ADR-3: Remove unused Pydantic models rather than integrate them

The `PlayerStats` model and `from_db_row()` factory are unused in production code. The app operates on raw DataFrames throughout. Rather than retrofit DataFrame-to-model conversion across the app (high effort, unclear benefit for a Streamlit toy app), remove the unused model. Keep `DifficultySettings` since it is used.

### ADR-4: Remove SQL injection validation

The app reads from a local CSV via pandas. There is no SQL database. The SQL injection regex in `src/validation/inputs.py` protects against a nonexistent threat. Remove it. Keep the character validation and search term length checks, which are still useful for input sanitization.

### ADR-5: Consolidate dependencies to pyproject.toml only

`requirements.txt` and `pyproject.toml` declare the same dependencies. Remove `requirements.txt` and update CI to install from `pyproject.toml`. Keep `requirements-dev.txt` only if it differs from `[project.optional-dependencies] dev`.

## Tech Stack

- **Runtime:** Python 3.11+ / Streamlit
- **ML:** TensorFlow/Keras (unchanged)
- **Data:** pandas DataFrames from local CSV
- **Validation:** Pydantic v2 (for DifficultySettings only, post-cleanup)
- **Testing:** pytest + pytest-cov
- **Linting:** ruff (lint + format)
- **Type checking:** mypy (strict mode)
- **CI:** GitHub Actions

## Testing Strategy

- All tests must run without a Streamlit runtime (no `streamlit run` needed).
- Mock `streamlit` imports where page modules are tested.
- Use `pytest` fixtures in `conftest.py` for shared test data (DataFrames, model mocks).
- Integration tests that load real CSV data are acceptable since the CSV is committed to the repo.
- No live external services; all network calls are mocked.
- Target coverage threshold: 70% (up from 50%).

## Commit Message Format

Use conventional commits:

```
type(scope): brief description
```

Types: `fix`, `feat`, `refactor`, `test`, `ci`, `docs`, `chore`

Scopes: `gitignore`, `dead-code`, `database`, `ml`, `validation`, `state`, `pages`, `ci`, `deps`, `readme`

Examples:
- `refactor(dead-code): remove unused GameState and dead functions`
- `fix(database): remove empty finally block in connection manager`
- `ci(deps): consolidate to pyproject.toml, remove requirements.txt`

## Shared Patterns

### Logging

Replace f-string logging with lazy `%s` formatting:
```python
# Before
logger.error(f"Error: {e}")
# After
logger.error("Error: %s", e)
```

### Imports

Keep `__init__.py` files with explicit `__all__` exports. When removing dead code, update both the source file and the corresponding `__init__.py`.

### Error Handling

Use specific exception types, not bare `except Exception`. Remove no-op `finally: pass` blocks.
