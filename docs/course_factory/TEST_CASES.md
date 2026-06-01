# Test cases

## TEST_CASES_20260601_V0_1

Course Factory must be tested before backend or UI development.

The first tests are file-based.

Each test must define:

- input source pack;
- target audience;
- course goal;
- expected artifact;
- acceptance criteria;
- STOP conditions.

## Test 1 — Source digest from project documents

Purpose:

Check whether Source Analyst can extract a useful source digest from project documentation.

Input:

- small source pack from Course Factory docs or OpenScript workflow docs.

Expected output:

- source digest with topics, procedures, vocabulary, risks, missing information, and human decisions.

Acceptance:

- does not write a course;
- does not invent missing source facts;
- identifies gaps and contradictions.

## Test 2 — Curriculum map from source digest

Purpose:

Check whether Course Architect can create a course map from a digest.

Input:

- approved source digest;
- course brief.

Expected output:

- curriculum map.

Acceptance:

- lessons have order rationale;
- every lesson has outcome, practice, and assessment idea;
- excluded topics are named.

## Test 3 — Lesson blueprint

Purpose:

Check whether Lesson Designer can create a practical lesson blueprint.

Input:

- curriculum map;
- selected lesson topic;
- source digest.

Expected output:

- lesson blueprint.

Acceptance:

- objective is measurable;
- learner action exists;
- assessment matches objective;
- common mistake and recovery are included.

## Test 4 — Lesson text

Purpose:

Check whether Lesson Writer can write a lesson from a blueprint without inventing facts.

Input:

- approved lesson blueprint;
- source digest.

Expected output:

- lesson text.

Acceptance:

- follows lesson text contract;
- does not change lesson objective;
- does not add unsupported facts.

## Test 5 — Assessment set

Purpose:

Check whether Assessment Designer can create aligned checks.

Input:

- lesson blueprint;
- lesson text.

Expected output:

- assessment set.

Acceptance:

- checks match objective;
- wrong answers reveal misconceptions;
- pass/fail rule is clear.

## Test 6 — Quality review

Purpose:

Check whether Quality Reviewer can reject weak lessons.

Input:

- intentionally weak lesson;
- course brief;
- rubric.

Expected output:

- quality review report.

Acceptance:

- rejects article-like lesson with no learner action;
- rejects definition-only assessment for practical objective;
- does not rewrite the lesson.

## Test 7 — Grounding review

Purpose:

Check whether Grounding Reviewer can find unsupported claims.

Input:

- lesson text;
- source digest.

Expected output:

- grounding review report.

Acceptance:

- identifies unsupported claims;
- separates source facts from instructional inferences;
- returns FAIL when evidence is missing.
