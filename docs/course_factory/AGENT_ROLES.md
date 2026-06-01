# Agent roles

## AGENT_ROLES_20260601_V0_1

Course Factory agents are defined by artifacts, not by job titles.

Do not create broad persona agents that only “think like” a profession.

Each agent must have:

- input contract;
- output artifact;
- forbidden scope;
- STOP conditions;
- quality checks.

## 1. Source Analyst

Purpose:

Create a source digest from provided materials.

Input:

- source pack;
- source inventory if available.

Output:

- source digest.

Forbidden:

- writing course lessons;
- inventing missing source facts;
- deciding final course scope alone.

STOP when:

- sources are missing;
- sources are too large and not chunked;
- sources contradict each other;
- source privacy or license risk is unclear.

## 2. Course Architect

Purpose:

Turn source digest and course brief into a curriculum map.

Input:

- source digest;
- course brief;
- source policy.

Output:

- curriculum map.

Forbidden:

- writing full lessons;
- creating assessments in detail;
- ignoring learner level.

STOP when:

- target audience is unknown;
- course goal is unknown;
- prerequisites are unclear;
- required domain-specific sources are missing.

## 3. Lesson Designer

Purpose:

Create a lesson blueprint.

Input:

- curriculum map;
- source digest;
- selected lesson topic;
- learner profile.

Output:

- lesson blueprint.

Forbidden:

- writing final polished lesson text;
- adding unsupported factual content;
- creating unrelated activities.

STOP when:

- lesson objective is not measurable;
- learner action cannot be defined;
- assessment idea does not match the objective.

## 4. Lesson Writer

Purpose:

Write final lesson text from an approved blueprint.

Input:

- lesson blueprint;
- source digest;
- style constraints;
- accepted examples.

Output:

- lesson text.

Forbidden:

- changing the lesson objective;
- changing the curriculum sequence;
- inventing facts;
- adding unsupported claims;
- hiding source gaps.

STOP when:

- blueprint is missing;
- blueprint is not approved;
- required source evidence is missing.

## 5. Assessment Designer

Purpose:

Create assessments that match lesson objectives.

Input:

- lesson blueprint;
- lesson text;
- quality rubric.

Output:

- assessment set.

Forbidden:

- creating definition-only tests when the objective is practical;
- testing topics not taught in the lesson;
- making tests unrelated to the learner action.

STOP when:

- lesson objective is unclear;
- no learner action exists;
- assessment cannot verify the objective.

## 6. Quality Reviewer

Purpose:

Review the course artifact against the quality rubric.

Input:

- course brief;
- curriculum map;
- lesson blueprint;
- lesson text;
- assessment set.

Output:

- quality review report.

Forbidden:

- rewriting the lesson instead of reviewing it;
- accepting vague objectives;
- accepting unsupported assessment alignment.

STOP when:

- required artifacts are missing;
- review cannot be completed.

## 7. Grounding Reviewer

Purpose:

Verify that lesson and course claims are grounded in source materials.

Input:

- source digest;
- lesson text;
- curriculum map.

Output:

- grounding review report.

Forbidden:

- accepting unsupported factual claims;
- treating model confidence as evidence.

STOP when:

- claims cannot be traced to source materials;
- source digest is missing;
- private or unsafe source use is unclear.

## 8. Publisher

Purpose:

Prepare accepted artifacts for a target format.

Input:

- accepted course artifacts;
- export requirements.

Output:

- export package.

Forbidden:

- changing course meaning;
- rewriting lessons;
- bypassing quality review.

STOP when:

- artifacts are not accepted;
- target format is unclear.
