# Course Factory method

## METHOD_20260601_V0_1

Course Factory is a source-grounded workflow for turning reference materials into educational courses.

It does not generate a full course in one uncontrolled step.

It uses a staged pipeline.

Canonical upstream handoff rules are defined in:

`docs/course_factory/PIPELINE_HANDOFF_CONTRACT.md`

Methodology reference governance is defined in:

`docs/course_factory/METHODOLOGY_REFERENCE_GOVERNANCE.md`

The accepted methodology references determine how the stages are designed, what the agent contracts require, and how the UI and quality gates are shaped.

## Pipeline

### 1. Source intake

Collect the source materials.

Inputs may include:

- project documentation;
- manuals;
- instructions;
- transcripts;
- policies;
- books;
- markdown files;
- repository documentation;
- lesson drafts.

Output:

- source pack folder;
- source inventory.

### 2. Source digest

Extract the core meaning of the source pack.

Output:

- source digest.

The source digest must identify what the material says, what is missing, what is risky, and what can be used.

### 3. Course brief

Define the course before designing lessons.

Output:

- course brief.

The course brief must define:

- target audience;
- course goal;
- learner starting level;
- course format;
- expected practical result;
- constraints;
- required domain sources;
- human approval points.

### 4. Curriculum map

Design the course sequence.

Output:

- curriculum map.

The curriculum map must define:

- modules or lessons;
- lesson order;
- prerequisites;
- outcome for each lesson;
- assessment idea for each lesson;
- difficulty progression.

### 5. Lesson blueprint

Design one lesson before writing final text.

Output:

- lesson blueprint.

The lesson blueprint must define:

- working situation;
- learner objective;
- previous knowledge;
- explanation blocks;
- learner action;
- example;
- practice task;
- assessment;
- common mistake;
- pass/fail criteria.

### 6. Lesson text

Write the lesson from the approved blueprint.

Output:

- lesson text.

The lesson text must not introduce unsupported facts.

### 7. Assessments

Create checks that match lesson objectives.

Output:

- assessment set.

Assessment must verify what the learner should be able to do, not only whether the learner remembers definitions.

### 8. Quality review

Review the course artifact against the rubric.

Output:

- quality review report.

The reviewer must return PASS or FAIL with reasons.

### 9. Grounding review

Check that course claims are grounded in source materials or explicitly marked as instructional inference.

Output:

- grounding review report.

### 10. Export

Prepare the accepted course for a target format.

Output:

- export package.

The first MVP does not implement export automation.

## Core rule

Every stage must create a concrete artifact.

No stage is accepted only because the agent says it is done.
