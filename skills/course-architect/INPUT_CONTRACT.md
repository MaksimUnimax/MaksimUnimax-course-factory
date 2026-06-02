# Course Architect input contract

## Required input package

Course Architect requires a complete input package.

Minimum required input:

1. accepted `source_digest.md`;
2. course brief;
3. target audience;
4. learner starting level;
5. course goal;
6. expected practical result;
7. source boundaries;
8. known missing information and human decisions.

## Required file: source digest

The run must include an accepted source digest.

Expected file name:

`source_digest.md`

The source digest must include enough information about:

- source inventory;
- main topics;
- key procedures;
- terms and vocabulary;
- target audience clues;
- safety constraints;
- contradictions;
- missing information;
- license/privacy concerns;
- usable source facts;
- instructional inferences;
- required human decisions;
- STOP status.

The digest must be accepted by the human/operator or explicitly marked as ready for the next stage.

If `source_digest.md` is missing, create `STOP_REPORT.md` with:

`STOP_SOURCE_DIGEST_MISSING`

If `source_digest.md` exists but is not accepted or has a failing STOP status, create `STOP_REPORT.md` with:

`STOP_SOURCE_DIGEST_NOT_ACCEPTED`

## Required course brief

The course brief tells the agent what course to design.

The course brief must define:

- course working title;
- target audience;
- learner starting level;
- course goal;
- expected practical result;
- course format or approximate size;
- scope boundaries;
- prerequisites;
- source basis;
- human approval points.

The course brief may be inside `RUN_REQUEST.md` or in a separate markdown file.

If the course brief is missing, create `STOP_REPORT.md` with:

`STOP_COURSE_BRIEF_MISSING`

## Required target audience

The target audience must be specific enough to design the course.

Acceptable examples:

- absolute beginners who are not programmers;
- junior developers who know Git basics;
- creators who can use ChatGPT but do not know server deployment;
- students who have never used terminal or GitHub.

Unacceptable examples:

- everyone;
- beginners, without saying beginners in what;
- users;
- people interested in AI.

If target audience is missing or too vague, create `STOP_REPORT.md` with:

`STOP_AUDIENCE_UNKNOWN`

## Required learner starting level

The learner starting level must describe what the learner already can and cannot do.

It should answer:

- does the learner know Git?
- does the learner know terminal?
- does the learner know server basics?
- does the learner know markdown?
- does the learner understand the difference between ChatGPT and Codex?
- does the learner understand source-of-truth documents?

If learner starting level is missing, create `STOP_REPORT.md` with:

`STOP_LEARNER_LEVEL_UNKNOWN`

## Required course goal

The course goal must describe the course result.

Good course goal format:

After this course, the learner will be able to do one observable practical action.

Examples:

- create and manage a small AI-assisted project through ChatGPT, Codex, server, and GitHub;
- prepare source-grounded course artifacts using a file-based agent workflow;
- run one controlled agent task and verify its output.

Bad course goals:

- understand AI;
- learn development;
- become better at prompts;
- get familiar with agents.

If the course goal is missing or not actionable, create `STOP_REPORT.md` with:

`STOP_COURSE_GOAL_UNKNOWN`

## Required expected practical result

The expected practical result must say what the learner will have created, configured, reviewed, or executed by the end.

Examples:

- a GitHub-backed project skeleton;
- a read-only project structure page;
- one accepted source digest;
- one accepted curriculum map;
- one controlled run report.

If the expected practical result is missing, create `STOP_REPORT.md` with:

`STOP_EXPECTED_RESULT_UNKNOWN`

## Required prerequisites

Prerequisites must say what must be true before the learner starts.

Examples:

- has a GitHub account;
- has access to a server;
- can open ChatGPT;
- can copy and paste commands;
- can upload markdown documents.

If prerequisites are unclear and this blocks lesson order, create `STOP_REPORT.md` with:

`STOP_PREREQUISITES_UNCLEAR`

## Optional input

Optional input may include:

- preferred number of lessons;
- preferred lesson length;
- preferred course tone;
- allowed terminology;
- forbidden terminology;
- example learner mistakes;
- examples of good and bad outputs;
- platform limitations;
- UI limitations;
- assessment style preference.

Optional input may improve the map, but the agent must not invent missing required input.

## Input validation checklist

Before creating `curriculum_map.md`, verify:

- [ ] `source_digest.md` exists.
- [ ] `source_digest.md` is accepted or marked ready.
- [ ] target audience is clear.
- [ ] learner starting level is clear.
- [ ] course goal is observable.
- [ ] expected practical result is clear.
- [ ] prerequisites are clear enough to order lessons.
- [ ] source gaps are visible.
- [ ] human decisions are visible.
- [ ] no required domain-specific source is missing.

If any required item fails, create `STOP_REPORT.md`.