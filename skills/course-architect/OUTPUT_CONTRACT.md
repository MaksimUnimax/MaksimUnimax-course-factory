# Course Architect output contract

## Successful output

When the input is sufficient, Course Architect must produce exactly this main artifact:

`curriculum_map.md`

`curriculum_map.md` means:

карта курса

The file must be markdown, file-based, and git-trackable.

## Blocked output

When the input is insufficient, Course Architect must produce:

`STOP_REPORT.md`

Do not invent missing information to avoid a STOP.

## Required structure of `curriculum_map.md`

Use this structure exactly.

# Curriculum map

`curriculum_map.md` здесь означает «карта курса».

## 1. Course identity

- Course title:
- Working course type:
- Target audience:
- Learner starting level:
- Course goal:
- Expected practical result:

## 2. Source basis

- Accepted source digest:
- Main source topics used:
- Main source procedures used:
- Important vocabulary used:
- Safety constraints carried forward:
- Source gaps carried forward:
- Human decisions carried forward:

## 3. Course shape

- Recommended number of lessons:
- Recommended lesson format:
- Recommended progression model:
- What the course is:
- What the course is not:

## 4. Lesson list

| Lesson | Title | Main purpose | Learner outcome | Source basis |
|---:|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |

## 5. Lesson order rationale

Explain why the lessons are ordered this way.

For each lesson, explain:

- why it comes at this point;
- what previous knowledge it depends on;
- what later lesson depends on it.

## 6. Prerequisite chain

| Lesson | Requires before this lesson | Enables after this lesson |
|---:|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

## 7. Outcome per lesson

Each outcome must describe an observable learner ability.

Bad:

- understand Git;
- learn agents;
- know how prompts work.

Good:

- create a public GitHub repository for the project;
- explain why `localhost` must not be shown as the learner-facing address;
- verify a Codex report against expected files.

| Lesson | Observable outcome |
|---:|---|
| 1 |  |
| 2 |  |
| 3 |  |

## 8. Practice per lesson

Each lesson must include a practical or simulated learner action.

| Lesson | Practice task direction |
|---:|---|
| 1 |  |
| 2 |  |
| 3 |  |

## 9. Assessment idea per lesson

Assessment ideas must be short. Do not write full test questions here.

| Lesson | Assessment idea |
|---:|---|
| 1 |  |
| 2 |  |
| 3 |  |

## 10. Difficulty progression

Explain how the course moves from easier to harder work.

Include:

- what is introduced first;
- when the learner starts doing practical work;
- where verification is introduced;
- where multi-step reasoning begins;
- what is intentionally delayed.

## 11. Topics excluded from MVP

| Excluded topic | Why excluded | Can be added later? |
|---|---|---|
|  |  |  |

## 12. Source gaps and human decisions carried forward

| Gap or decision | Why it matters | Who must resolve it | Suggested timing |
|---|---|---|---|
|  |  |  |  |

## 13. Risks

List risks that could make the course confusing, unsafe, too advanced, or insufficiently grounded.

For each risk, include a mitigation.

| Risk | Mitigation |
|---|---|
|  |  |

## 14. Readiness for next agent

State whether this map is ready for Lesson Designer.

Use one status:

- `PASS_CURRICULUM_MAP_READY`
- `NEEDS_HUMAN_DECISION_BEFORE_LESSON_DESIGN`
- `STOPPED`

## 15. STOP status

If successful, use:

`PASS_CURRICULUM_MAP_READY`

If not successful, do not pretend success. Produce `STOP_REPORT.md`.

## Required rules for lesson list

The lesson list must:

- start from the learner’s real starting level;
- avoid assuming knowledge not yet taught;
- build toward the expected practical result;
- keep each lesson focused on one main learner action;
- separate setup, explanation, action, and verification where needed;
- carry source gaps forward instead of hiding them.

## Required rules for outcomes

Each lesson outcome must be observable.

Use verbs like:

- create;
- configure;
- compare;
- verify;
- explain why;
- identify;
- fix;
- review;
- submit;
- update.

Avoid vague verbs like:

- understand;
- know;
- learn;
- get familiar with.

## Required rules for practice

Each practice idea must be something the learner can do or simulate.

Good practice examples:

- create a repo;
- inspect a file tree;
- compare a report with expected files;
- identify a missing source;
- choose the correct next step;
- rewrite a vague course goal into an observable one.

Bad practice examples:

- read the material;
- think about the topic;
- understand the concept.

## Required rules for assessment ideas

Assessment ideas must match the lesson outcome.

If the outcome is practical, the assessment idea must be practical or scenario-based.

Do not create detailed questions in this artifact. Detailed assessment belongs to Assessment Designer.

## Required rules for excluded topics

Excluded topics are not failures. They are MVP boundaries.

Exclude topics when they are:

- unsupported by source materials;
- too advanced for the target learner;
- not needed for the first practical result;
- risky without domain-specific source;
- better handled in a later course.

## Required rules for source gaps

Do not hide gaps from Source Analyst.

If the source digest says something is missing, Course Architect must either:

1. design around it;
2. exclude the affected topic from MVP;
3. mark it as a human decision;
4. stop if it blocks the map.

## Required `STOP_REPORT.md` structure

When blocked, write this structure:

# STOP report

## STOP labels

- STOP_...

## Why stopped

Explain the blocking issue briefly.

## Missing or unsafe input

List exactly what is missing, unclear, contradictory, unsafe, or not approved.

## What can be done next

List the minimal human or upstream action needed.

## What was not done

Confirm that Course Architect did not:

- write full lessons;
- invent missing source facts;
- create detailed assessments;
- ignore source gaps.