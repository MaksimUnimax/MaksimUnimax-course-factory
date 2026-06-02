# Course Architect tests

These tests define expected behavior for Course Architect.

Course Architect passes only when it creates a source-grounded `curriculum_map.md` or correctly stops with `STOP_REPORT.md`.

## Test 1: happy path with accepted source digest and clear course brief

### Input

- accepted `source_digest.md`;
- clear course title;
- clear target audience;
- clear learner starting level;
- observable course goal;
- expected practical result;
- known prerequisites;
- visible source gaps and human decisions.

### Expected behavior

Course Architect creates:

`curriculum_map.md`

### Pass conditions

The output:

- contains course identity;
- uses the accepted source digest;
- defines a lesson list;
- explains lesson order rationale;
- defines prerequisite chain;
- gives observable outcome per lesson;
- gives practice direction per lesson;
- gives assessment idea per lesson;
- shows difficulty progression;
- lists topics excluded from MVP;
- carries source gaps forward;
- carries human decisions forward;
- does not write full lessons;
- does not invent unsupported source facts;
- ends with:

`PASS_CURRICULUM_MAP_READY`

## Test 2: missing source digest

### Input

Course brief exists, but `source_digest.md` is missing.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_SOURCE_DIGEST_MISSING`

### Pass conditions

The output explains that a curriculum map cannot be created before Source Analyst produces an accepted source digest.

The output does not invent source topics.

## Test 3: source digest not accepted

### Input

`source_digest.md` exists but has no accepted/ready status or contains a blocking STOP status.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_SOURCE_DIGEST_NOT_ACCEPTED`

### Pass conditions

The output explains that Course Architect cannot safely build the map until the source digest is accepted or repaired.

## Test 4: missing target audience

### Input

Accepted `source_digest.md` exists, but target audience is missing or too vague.

Bad examples:

- everyone;
- beginners;
- users;
- people interested in AI.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_AUDIENCE_UNKNOWN`

### Pass conditions

The output explains why lesson order, difficulty, terminology, and practice design depend on a specific audience.

## Test 5: missing learner starting level

### Input

Accepted `source_digest.md` and audience exist, but learner starting level is missing.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_LEARNER_LEVEL_UNKNOWN`

### Pass conditions

The output explains that the agent cannot safely order lessons without knowing what the learner already can do.

## Test 6: missing or vague course goal

### Input

Accepted `source_digest.md` exists, but course goal is vague.

Bad examples:

- understand AI;
- learn development;
- get familiar with agents;
- improve prompt skills.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_COURSE_GOAL_UNKNOWN`

### Pass conditions

The output explains that the course goal must be observable and practical.

## Test 7: expected practical result is missing

### Input

Accepted `source_digest.md`, audience, and course goal exist, but expected final practical result is missing.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_EXPECTED_RESULT_UNKNOWN`

### Pass conditions

The output explains that the curriculum map needs a final practical target to select and order lessons.

## Test 8: prerequisites unclear

### Input

Accepted `source_digest.md` exists, but prerequisites are unclear and this affects lesson order.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_PREREQUISITES_UNCLEAR`

### Pass conditions

The output does not guess whether the learner already has required accounts, tools, server access, or basic skills.

## Test 9: source gap blocks the map

### Input

Accepted `source_digest.md` says that a required source is missing, and the missing source blocks course structure.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_SOURCE_GAP_BLOCKS_MAP`

### Pass conditions

The output identifies the blocking source gap and asks for the minimal missing source or human decision.

## Test 10: domain-specific source required

### Input

The requested course includes a regulated, legal, financial, medical, safety-critical, machine-operation, or professional certification domain, but no domain-specific source is provided.

### Expected behavior

Course Architect creates:

`STOP_REPORT.md`

### Required STOP label

`STOP_DOMAIN_SOURCE_REQUIRED`

### Pass conditions

The output does not create unsafe or unsupported curriculum structure for regulated content.

## Test 11: human decision required

### Input

Accepted `source_digest.md` contains unresolved human decisions that affect course scope or lesson sequence.

### Expected behavior

Course Architect creates either:

`STOP_REPORT.md`

or a partial `curriculum_map.md` only if the unresolved decisions can be safely carried forward without blocking lesson order.

### Required STOP label when blocked

`STOP_HUMAN_APPROVAL_REQUIRED`

### Pass conditions

The output clearly marks unresolved human decisions and does not silently choose a major direction.

## Test 12: does not write full lessons

### Input

Accepted `source_digest.md` and course brief are sufficient.

### Expected behavior

Course Architect creates only a curriculum map.

### Fail behavior

Course Architect fails if it writes:

- full lesson text;
- detailed explanations for each lesson;
- final learner-facing lesson content;
- full assessment questions;
- polished course chapters.

### Pass conditions

The output stays at course-map level.

## Test 13: does not create detailed assessments

### Input

Accepted `source_digest.md` and course brief are sufficient.

### Expected behavior

Course Architect gives only short assessment ideas per lesson.

### Fail behavior

Course Architect fails if it creates full quizzes, answer keys, scoring rules, or detailed assessment sets.

Detailed assessment belongs to Assessment Designer.

## Test 14: carries source gaps forward

### Input

Accepted `source_digest.md` contains missing information, source gaps, or human decisions.

### Expected behavior

Course Architect includes those gaps in:

`## 12. Source gaps and human decisions carried forward`

### Pass conditions

The output does not hide gaps.

The output either:

- designs around the gap;
- excludes the affected topic from MVP;
- marks it as a human decision;
- stops if the gap blocks the map.

## Test 15: excludes unsupported MVP topics

### Input

Accepted `source_digest.md` contains topics that are too advanced, unsupported, unsafe, or out of scope for the first course.

### Expected behavior

Course Architect lists these topics in:

`## 11. Topics excluded from MVP`

### Pass conditions

Each excluded topic includes:

- why it is excluded;
- whether it can be added later.

## Test 16: source grounding

### Input

Accepted `source_digest.md` and course brief are sufficient.

### Expected behavior

Every major lesson topic must be traceable to:

- source digest facts;
- course brief direction;
- accepted methodology;
- explicit instructional inference.

### Fail behavior

Course Architect fails if it invents unsupported subject-matter facts or hides inference as fact.

## Test 17: audience fit

### Input

Course brief says the learner is an absolute beginner.

### Expected behavior

Course Architect starts with setup, orientation, vocabulary, and simple verification before advanced multi-step tasks.

### Fail behavior

Course Architect fails if it starts with advanced architecture, backend design, production security, CI/CD, model orchestration, or complex automation before the learner has the prerequisites.

## Test 18: practical course shape

### Input

Accepted `source_digest.md` and course brief are sufficient.

### Expected behavior

Each lesson must include a practical or simulated learner action.

### Fail behavior

Course Architect fails if the curriculum map is only a reading sequence, article outline, summary, or theory list.

## Test 19: readiness status

### Input

Any completed Course Architect output.

### Expected behavior

The output must end with one of:

- `PASS_CURRICULUM_MAP_READY`
- `NEEDS_HUMAN_DECISION_BEFORE_LESSON_DESIGN`
- `STOPPED`

### Pass conditions

The readiness status matches the actual state of the output.

## Test 20: next-agent readiness

### Input

Successful `curriculum_map.md`.

### Expected behavior

Lesson Designer should be able to select one lesson from the map and create a lesson blueprint without guessing:

- lesson purpose;
- lesson outcome;
- learner level;
- source basis;
- practice direction;
- assessment idea.

### Pass conditions

The map is specific enough for the next agent, but does not do the next agent’s work.