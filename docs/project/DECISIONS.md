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

Canonical pipeline architecture uses single-upload upstream artifact handoff:

- source intake happens once;
- downstream agents consume previous artifacts from the workflow chain;
- manual ChatGPT-made re-upload archives are not canonical pipeline proof.

The accepted methodology references are the working methodology base for Course Factory:

- skill docs;
- starting questions;
- artifact contracts;
- tests;
- quality gates;
- UI field sets.

Those elements must be derived from the accepted methodology references and updated through the documented governance process, not from the current test topic.

The initial `/runs` course setup is a dropdown-only universal model:

- uploaded source documents define the subject and facts;
- dropdowns define course design choices;
- free-text course setup fields are not part of this slice.

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

## 2026-06-02 — Upstream artifact handoff is canonical

The canonical pipeline architecture is single-upload upstream artifact handoff.

Decision:

- source intake happens once;
- downstream agents must consume previous artifacts from the workflow chain;
- manual ChatGPT-made re-upload archives are allowed only for isolated upload/UI tests, not as canonical pipeline proof;
- downstream run creation should carry upstream lineage explicitly, not rely on ad-hoc re-uploaded artifacts.

## 2026-06-02 — Course setup UI creates the course brief

The structured `/runs` intake form is the canonical source of course setup.

Decision:

- the initial Source Analyst intake saves structured course settings once;
- the intake creates `course_setup.json` and `output/course_brief.md` as workflow artifacts;
- `course_brief.md` is a human/workflow artifact, not an agent output;
- downstream agents consume the saved course brief through upstream handoff instead of a fresh ChatGPT-made upload archive.

The methodology-reference governance doc is part of the canonical documentation set:

- `docs/course_factory/METHODOLOGY_REFERENCE_GOVERNANCE.md`
