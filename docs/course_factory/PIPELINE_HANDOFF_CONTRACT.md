# Pipeline handoff contract

## PIPELINE_HANDOFF_CONTRACT_20260602_V0_1

Course Factory uses a staged, upstream-handoff pipeline.

This contract exists to prevent ad-hoc re-upload archives from becoming the canonical way to pass artifacts between agents.

## Canonical pipeline rule

1. The user uploads source documents once at initial source intake.
2. Source Analyst consumes that source pack and creates `source_digest.md`.
3. Course Architect consumes the accepted `source_digest.md` plus the course brief artifact.
4. Course Architect creates `curriculum_map.md`.
5. Lesson Designer consumes `curriculum_map.md` plus the required upstream artifacts.
6. Later agents consume the prior artifact chain in order.

## Single source intake

Initial uploaded source documents belong to the workflow source pack.

They are reused by later stages through references or controlled copied artifacts in the run chain.

They are not re-uploaded as new ChatGPT-made archives for downstream agent handoff.

## Upstream artifact handoff

Each downstream agent must receive required inputs from:

- previous run artifacts;
- project-level course artifacts;
- accepted artifacts in the workflow chain.

Downstream agents must not require the user to manually assemble a fresh upload archive of already-generated artifacts to prove the pipeline.

## Accepted artifact chain

- Source Analyst produces `source_digest.md`
- Course Architect consumes accepted `source_digest.md` plus the course brief artifact
- Course Architect produces `curriculum_map.md`
- Lesson Designer consumes `curriculum_map.md` plus required upstream artifacts
- Later agents consume the approved artifact chain in order

## Course brief handling

The course brief must exist as a workflow or project artifact.

If the course brief is missing, Course Architect must STOP with `STOP_COURSE_BRIEF_MISSING`.

Course Architect must not require a new ad-hoc ChatGPT upload archive to supply a missing brief.

## Manual uploads are not canonical pipeline proof

Manually uploading a ChatGPT-made archive may be used only for:

- isolated UI/upload testing;
- technical proof of archive handling;
- one-off inspection of upload behavior.

Manual uploads are not canonical proof of the downstream pipeline.

## Zip upload scope

Zip upload is allowed only as a convenience for:

- initial source intake;
- source pack upload;
- isolated upload tests.

Zip upload must not be the normal mechanism for passing generated artifacts between agents.

## Future `/runs` requirement

The `/runs` workflow should record upstream run lineage explicitly.

Future `/runs` handoff should support something like:

- `upstream_run_id`
- upstream artifact references
- automatic reuse of prior artifacts in the next run

Until that exists, downstream pipeline execution must not be claimed as fully automated artifact handoff.

## ChatGPT rule

ChatGPT must not generate upload archives as downstream agent inputs except for:

- primary source intake;
- explicit isolated upload tests.

## Canonical vs non-canonical proof

The existence of a manual/upload-based downstream run is useful evidence that the agent contract works.

It is not sufficient as canonical pipeline proof.

Canonical proof requires upstream artifact handoff in the workflow chain.
