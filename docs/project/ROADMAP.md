# Roadmap

## Stage 0 — Separate Course Factory repo and deploy key

Status: completed.

Created isolated repository, deploy key, initial documentation skeleton, and public GitHub push.

## Stage 1 — Methodology baseline v0.1

Status: completed.

Defined the Course Factory method, method sources, source policy, agent roles, artifact contracts, quality rubric, examples, and test cases.

## Stage 2 — Agent documents and editable admin MVP

Status: completed.

Created initial agent directories and markdown contracts.

Created admin UI for:

- viewing agent documents;
- editing markdown;
- uploading/replacing markdown;
- viewing git status.

## Stage 3 — Public Basic Auth live admin

Status: completed.

Admin MVP is available at:

`http://78.17.68.165:8091/`

The admin is protected by HTTP Basic Auth.

This is MVP security only, not a production-grade security model.

## Stage 4 — Selected-agent run request UI

Status: completed.

The `/runs` page creates selected-agent run requests.

The UI does not execute Codex/model calls.

The UI does not run all agents.

A run request stores uploaded source materials under:

`runs/<run_id>/input/source_pack/`

Expected outputs are written by separate controlled Codex runs under:

`runs/<run_id>/output/`

## Stage 5 — First Source Analyst controlled execution

Status: completed.

Completed run:

`20260601_102242_source-analyst`

Output:

`runs/20260601_102242_source-analyst/output/source_digest.md`

Result:

`completed_success`

## Stage 6 — Source Analyst result review

Status: current.

Review the first `source_digest.md`.

Decide whether it is acceptable for Course Architect or whether Source Analyst contracts need stricter source traceability.

## Stage 7 — Course Architect controlled execution

Status: next after review.

Use the accepted source digest to create a curriculum map.

## Stage 8 — `/runs` upstream artifact handoff

Status: partial.

Implemented for the first slice:

- completed Source Analyst run -> pending Course Architect run;
- controlled copy of upstream `source_digest.md`;
- controlled copy of upstream `course_brief.md` when the intake created it;
- explicit `upstream_run_id` and `input_mode` in the downstream run.

Next: extend the same pattern to later agents and project-level course artifacts.

## Stage 9 — Additional agents one by one

Status: later.

Add and test:

- Lesson Designer;
- Lesson Writer;
- Assessment Designer;
- Quality Reviewer;
- Grounding Reviewer;
- Publisher.

## Stage 10 — Real backend/tool architecture

Status: later.

Only after the file-based workflow quality is proven, design a real server/tool architecture.
