# Run request

## Run ID

20260602_100613_course-architect

## Agent

course-architect

## Status

pending_codex_execution

## Input mode

upstream_artifact_handoff

## Upstream run ID

20260601_102242_source-analyst

## Upstream agent

source-analyst

## Target agent

course-architect

## Upstream artifact source path

output/source_digest.md

## Local copied artifact path

input/upstream_artifacts/20260601_102242_source-analyst/source_digest.md

## Inherited context

# Run request

## Run ID

20260601_102242_source-analyst

## Agent

source-analyst

## Status

pending_codex_execution

## Goal

Разобрать исходный документ OpenScript Agent Lab Student Kit и подготовить разбор исходных материалов для будущего курса.

## Target audience

Новичок без опыта программирования, который учится работать через ChatGPT + Codex + сервер + GitHub.

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

## Course brief status

missing

## Expected execution behavior

Course Architect may STOP with STOP_COURSE_BRIEF_MISSING unless a course brief artifact is provided by workflow/project setup.

## Execution rule

This run request was created by the upstream artifact handoff workflow.

The UI does not execute Codex or model calls.

A separate controlled Codex run must read this request, execute only the selected agent, and write results to:

`output/`
