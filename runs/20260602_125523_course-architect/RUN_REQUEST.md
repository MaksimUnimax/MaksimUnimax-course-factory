# Run request

## Run ID

20260602_125523_course-architect

## Agent

course-architect

## Status

pending_codex_execution

## Input mode

upstream_artifact_handoff

## Upstream run ID

20260602_124454_source-analyst

## Upstream agent

source-analyst

## Target agent

course-architect

## Upstream artifacts

- source_digest.md
  - Upstream source path: output/source_digest.md
  - Local copied artifact path: input/upstream_artifacts/20260602_124454_source-analyst/source_digest.md
- course_brief.md
  - Upstream source path: output/course_brief.md
  - Local copied artifact path: input/upstream_artifacts/20260602_124454_source-analyst/course_brief.md

## Inherited context

# Run request

## Run ID

20260602_124454_source-analyst

## Agent

source-analyst

## Status

pending_codex_execution

## Goal

—

## Target audience

—

## Source files

- input/source_pack/openscript_agent_lab_student_kit_source.md

## Execution rule

This run request was created by the admin UI.

The UI does not execute Codex or model calls.

A separate controlled Codex run must read this request, execute only the selected agent, and write results to:

`output/`

## Expected output for source-analyst

If agent is `source-analyst`, expected output is:

`output/source_digest.md`

## Course setup

Эти настройки сохраняются как "Задание на курс" и передаются следующим агентам автоматически.

## Course setup path

course_setup.json

## Course brief status

available

## Course brief path

output/course_brief.md

## Course setup source

ui_dropdowns

## Subject source

uploaded_source_documents

## Methodology source

accepted_course_factory_methodology_references

## Course brief status

available

## Expected execution behavior

Course Architect can proceed if the upstream course brief artifact is available in the workflow chain.

## Execution rule

This run request was created by the upstream artifact handoff workflow.

The UI does not execute Codex or model calls.

A separate controlled Codex run must read this request, execute only the selected agent, and write results to:

`output/`
