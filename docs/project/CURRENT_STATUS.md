# Current status

Course Factory is in the file-based agent/skill test bench stage.

## Current proven state

- local repo: `/opt/course-factory`
- public repo: `https://github.com/MaksimUnimax/MaksimUnimax-course-factory`
- branch: `main`
- admin live URL: `http://78.17.68.165:8091/`
- auth mode: HTTP Basic Auth
- agent markdown editor: available
- selected-agent run request UI: available at `/runs`
- actual Codex/model execution from web UI: disabled by design
- run output viewer: available
- first tested agent: `source-analyst`

## Latest completed technical state

The `/runs` UI bugfix has been completed.

Fixed:

- `/api/runs`, `/api/runs/detail`, and `/api/runs/file` now return consistent success shape;
- API errors are clearer;
- selected agent, goal, and target audience are preserved as a browser draft;
- the UI explains that file inputs must be selected again after refresh.

The first controlled Source Analyst run has been completed.

Run:

`20260601_102242_source-analyst`

Input:

`runs/20260601_102242_source-analyst/input/source_pack/openscript_agent_lab_student_kit_source.md`

Output:

`runs/20260601_102242_source-analyst/output/source_digest.md`

Status:

`completed_success`

The Source Analyst result is a `source_digest.md`, meaning “разбор исходных материалов”.

The run did not write a course, did not write lessons, did not create a curriculum map, and did not execute other agents.

## Current active block

Review the first Source Analyst output and decide whether it is good enough to use as input for the next agent.

## Current blocker

Before running Course Architect, the user and ChatGPT must review `source_digest.md`.

Known quality concern:

The first Source Analyst output is useful for a first proof, but it is still high-level. The next iteration may need stronger source traceability: each key conclusion should be tied to a source section or source file.

## Next recommended step

Review the output:

`runs/20260601_102242_source-analyst/output/source_digest.md`

Then decide one of:

1. accept it and create a controlled `Course Architect` run;
2. improve the Source Analyst contracts to require stronger source traceability;
3. rerun Source Analyst with a stricter output requirement.
