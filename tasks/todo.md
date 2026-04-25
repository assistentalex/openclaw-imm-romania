# prompt-to-pr — ♻️ Refactor
**Date:** 2026-04-25 02:25
**Task:** Add `--json` flag to all nexlink commands for consistent output
**Branch:** night-shift/2026-04-25-Add---json-flag-to-all-nexl

---

## Preflight
- Git: ✅
- Tests: ✅ (pytest, 66 baseline)
- Conventions (SKILL.md): ⚠️ not found
- hardshell: ⚠️ not installed

## Context Summary
- Language: Python
- Core files: `modules/exchange/{utils,mail,cal,tasks,analytics,sync,cli}.py`, `modules/nextcloud/nextcloud.py`, `scripts/nexlink.py`
- Tests: `tests/test_all.py`, `tests/test_nextcloud.py`

## Plan Metadata
- Overall Risk: LOW
- Confidence: HIGH
- Blast Radius: narrow (additive flag, no existing behavior changed)
- Rollback: easy
- Unknowns: none
- Fast Path: yes

## Tasks
- [x] 1. Add `add_json_argument()` helper to `modules/exchange/utils.py` — Risk: LOW
- [x] 2. Add `--json` flag to all Exchange module subparsers (mail/cal/tasks/analytics/sync) — Risk: LOW
- [x] 3. Add `--json` flag to `cli.py` main and module parsers — Risk: LOW
- [x] 4. Add `--json` support to `modules/nextcloud/nextcloud.py` (runtime flag + JSON output in print functions) — Risk: LOW
- [x] 5. Update `scripts/nexlink.py` help text — Risk: LOW
- [x] 6. Add tests for `--json` flag presence — Risk: LOW
- [x] 7. Run full test suite — passed: 67/67

## Test Plan
- Run existing suite before changes (baseline): ✅ 66 passed
- Write new tests for: `--json` flag in CLI help output
- Run suite again after changes: ✅ 67 passed

## Completed Tasks
1. ✅ `modules/exchange/utils.py` — Added `add_json_argument()` with argparse import
2. ✅ `modules/exchange/mail.py` — Added import + call after each subparser set_defaults + main parser
3. ✅ `modules/exchange/cal.py` — Same pattern
4. ✅ `modules/exchange/tasks.py` — Same pattern
5. ✅ `modules/exchange/analytics.py` — Same pattern
6. ✅ `modules/exchange/sync.py` — Same pattern
7. ✅ `modules/exchange/cli.py` — Import + add to main parser + each module parser
8. ✅ `modules/nextcloud/nextcloud.py` — Added `_JSON_OUTPUT` flag, `--json` detection in `run_cli()`, JSON-aware `print_list/print_info/print_shared/print_share_links`
9. ✅ `tests/test_all.py` — Added `test_cli_help_json_flag_listed_in_subcommands`

## Test Results
All 67 tests pass (66 baseline + 1 new).

## Verify Summary
- `python3 -m modules.exchange.cli --help` shows `--json`
- `python3 -m modules.exchange.cli mail connect --help` shows `--json`
- All subcommand help outputs include `--json`
- Nextcloud `run_cli` detects `--json` and routes print functions to JSON output
- Exchange modules accept `--json` (already JSON via `out()`, flag is additive)
