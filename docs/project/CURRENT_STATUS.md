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
- source upload: `.md`, `.zip`, and mixed `.md` + `.zip` source intake
- course setup model: dropdown-only and topic-agnostic
- upstream handoff: implemented for completed Source Analyst run -> pending Course Architect run
- methodology-reference governance: documented
- pipeline handoff contract: documented

## Current completed proof chain

### Source Analyst proof

Run:

`20260602_124454_source-analyst`

Commit:

`72816db921971b26097422b801ed052ecdcabdd4`

Input:

`runs/20260602_124454_source-analyst/input/source_pack/openscript_agent_lab_student_kit_source.md`

Workflow artifact created by UI:

`runs/20260602_124454_source-analyst/output/course_brief.md`

Agent output:

`runs/20260602_124454_source-analyst/output/source_digest.md`

Status:

`PASS_SOURCE_DIGEST_READY`

Meaning:

`source_digest.md` = разбор исходных материалов.

The run did not write a course, did not write lessons, did not create a curriculum map, and did not execute other agents.

### Course Architect proof

Run:

`20260602_125523_course-architect`

Commit:

`8a6f25cfab60402905ed745c68b9497f42872bab`

Input mode:

`upstream_artifact_handoff`

Upstream run:

`20260602_124454_source-analyst`

Upstream artifacts:

- `input/upstream_artifacts/20260602_124454_source-analyst/source_digest.md`
- `input/upstream_artifacts/20260602_124454_source-analyst/course_brief.md`

Agent output:

`runs/20260602_125523_course-architect/output/curriculum_map.md`

Status:

`PASS_CURRICULUM_MAP_READY`

Meaning:

`curriculum_map.md` = карта курса.

The run did not write lessons, did not create assessment files, did not execute Lesson Designer, and did not change app/docs/skills/tests.

## Current active block

Course Factory file-based agent/skill test bench.

The first two artifact stages are proven:

```text
source material + dropdown-only course setup
→ Source Analyst
→ source_digest.md
→ Course Architect through upstream handoff
→ curriculum_map.md
```
