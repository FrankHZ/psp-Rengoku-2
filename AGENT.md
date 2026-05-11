# Agent Guide

## Operating Mode

Work autonomously by default. Aim for larger useful deliverables rather than
small stop-and-report loops. Stop only when there is a real blocker, a risky
choice that cannot be inferred from repo context, or a PPSSPP observation that
only the user can provide.

Use sub-agents for parallel work when the task naturally splits into independent
tracks, especially:

```text
font/rendering experiments
record discovery and reporting
translation batch processing
build verification and cleanup
```

Keep sub-agent tasks concrete, with clear file ownership when code changes are
involved.

## Documentation Discipline

Document all meaningful work items. If a local ignored artifact is useful,
record it in `docs/local-artifacts.md`. If it is no longer useful, remove it.
Do not let old generated builds pile up.

Keep `docs/chs-plan.md` short and current. Detailed historical observations
belong in targeted docs, seed CSVs, local summary JSON/CSV files, or git
history.

Keep the full documentation map in `README.md`; keep this file focused on agent
operating rules and documentation discipline.

## Mutable Project Rules

Keep this file stable. Put current strategy, translation policy, and layout
rules in the mutable docs:

```text
docs/chs-strategy.md
docs/chs-layout-rules.md
docs/chs-plan.md
```

## Git And Safety

Never revert user changes unless explicitly asked. Before destructive cleanup,
verify paths stay inside the workspace/local artifact area. Prefer native
PowerShell file operations on Windows and avoid cross-shell deletion pipelines.

Run the Python test suite after code/tooling changes:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Commit only when the user asks or when a natural milestone is complete and the
scope is clear.
