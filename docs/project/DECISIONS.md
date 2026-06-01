# Decisions

## 2026-06-01

Course Factory starts as a separate repository and project.

The first goal is to prove agent/skill methodology before building backend or UI.

Editing and documentation are done through Codex and Git.

Course Factory must not create courses from imagination. It must use source materials, explicit methodology sources, marked instructional inferences, and human approval.

The initial methodology baseline uses:

- The Carpentries;
- Open University Learning Design;
- Quality Matters;
- Rebus/OER approach.

Agent roles are artifact-based, not broad persona titles.

UI editing risk is accepted for `.md` documents, but edit scope is limited.

Public admin with Basic Auth is acceptable for MVP only.

Browser UI must not execute arbitrary shell commands.

Browser UI must not execute Codex/model calls in the current MVP.

The UI creates selected-agent run requests only.

One run request means one selected agent.

Source materials go to:

`runs/<run_id>/input/source_pack/`

Agent instructions and contracts live in:

`skills/<agent>/`

Result files live in:

`runs/<run_id>/output/`

The first tested agent is `Source Analyst`.

The first tested output is `source_digest.md`, but user-facing copy should explain it as “разбор исходных материалов”.

Existing old projects are no-touch in Course Factory workflow.

Hand-edited UI changes should be followed by a small commit/push Codex-run to avoid dirty working tree mixing.

## 2026-06-01 — First Source Analyst proof

The first selected-agent controlled run was completed successfully.

Run:

`20260601_102242_source-analyst`

Agent:

`source-analyst`

Input:

`openscript_agent_lab_student_kit_source.md`

Output:

`source_digest.md`

Result:

`completed_success`

The first proof confirmed that Source Analyst can create a source digest without writing a course, lessons, or curriculum map.

The next decision is whether this first digest is acceptable for Course Architect or whether Source Analyst needs a stricter traceability requirement before continuing.
