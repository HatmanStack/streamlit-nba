# Audit Remediation Plan: streamlit-nba

## Overview

This plan addresses findings from three audits of the streamlit-nba repository: a codebase health audit (3 critical, 6 high, 8 medium, 5 low findings), a 12-pillar evaluation (overall grade B, git hygiene at 5/10), and a documentation audit (4 drift, 5 gaps). The repository is a Streamlit-based NBA team builder and game prediction app using TensorFlow/Keras with a local CSV data source.

The remediation is sequenced as: cleanup first (remove dead code, unused dependencies, artifacts), then structural fixes (architecture, error handling, validation, testing), then guardrails (CI hardening, pre-commit hooks, type safety), and finally documentation corrections.

All work targets the existing codebase. No new features are introduced. The goal is to raise pillar scores toward 9/10 across the board while reducing the tech debt ledger to zero critical and zero high findings.

## Prerequisites

- Python 3.11+ (3.13 in dev environment)
- `uv` for package management
- Git
- Familiarity with: Streamlit, pandas, TensorFlow/Keras, Pydantic, pytest, ruff, mypy

## Phase Summary

| Phase | Tag | Goal | Token Estimate |
|-------|-----|------|----------------|
| 0 | -- | Foundation: architecture decisions, conventions, testing strategy | ~5k |
| 1 | [HYGIENIST] | Dead code removal, artifact cleanup, .gitignore, unused exports | ~20k |
| 2 | [IMPLEMENTER] | Architecture fixes: decouple Streamlit, fix error handling, validation, input guards | ~30k |
| 3 | [IMPLEMENTER] | Testing improvements: new tests, coverage threshold, integration tests | ~20k |
| 4 | [FORTIFIER] | CI hardening, pre-commit hooks, dependency consolidation, type rigor | ~20k |
| 5 | [DOC-ENGINEER] | README corrections, project structure docs, config documentation | ~15k |

## Navigation

- [Phase-0.md](Phase-0.md) - Foundation (all phases)
- [Phase-1.md](Phase-1.md) - [HYGIENIST] Cleanup
- [Phase-2.md](Phase-2.md) - [IMPLEMENTER] Architecture and code fixes
- [Phase-3.md](Phase-3.md) - [IMPLEMENTER] Testing improvements
- [Phase-4.md](Phase-4.md) - [FORTIFIER] Guardrails
- [Phase-5.md](Phase-5.md) - [DOC-ENGINEER] Documentation
- [feedback.md](feedback.md) - Review feedback tracking
