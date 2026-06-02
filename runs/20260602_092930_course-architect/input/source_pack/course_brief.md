# Course brief

## Course working title

Как новичку управлять AI-разработкой через ChatGPT, Codex, сервер и GitHub

## Course type

Практический вводный курс для абсолютного новичка.

## Target audience

Абсолютные новички, которые не являются программистами.

Ученик может:

- пользоваться ChatGPT;
- читать простые инструкции на русском;
- копировать и вставлять текст;
- открыть браузер;
- загрузить файл через UI.

Ученик может не знать:

- Git;
- GitHub;
- SSH;
- сервер;
- терминал;
- API;
- deploy key;
- markdown;
- difference between ChatGPT and Codex;
- что такое source-of-truth документы.

## Learner starting level

Learner starts from zero technical confidence.

Assume:

- no programming background;
- no command-line confidence;
- no Git/GitHub workflow knowledge;
- no server administration knowledge;
- no prior Codex workflow knowledge;
- no understanding of agent/tool separation.

The course must introduce concepts only when they become practically necessary.

## Course goal

After this course, the learner will be able to run a small AI-assisted development workflow where ChatGPT designs the next step, Codex executes one bounded task, the server stores the project, GitHub preserves source history, and the learner verifies the result before moving forward.

## Expected practical result

By the end of the course, the learner should have:

- a public GitHub repository for a training project;
- a server-side project folder connected to Git;
- a basic source-of-truth documentation structure;
- a first controlled Codex report;
- a read-only project structure preview available through a public IP;
- a simple understanding of the difference between an agent and a tool;
- a repeatable one-step workflow: plan → execute → verify → commit/push → report.

## Preferred course size

Start with an MVP course of 6 to 8 lessons.

Do not design a long academy program yet.

## Course language

Russian.

Use simple explanations.

Avoid heavy jargon unless the term is necessary for the workflow.

When a technical term is necessary, explain it briefly in practical language.

## Course tone

Calm, practical, direct.

The course should not shame the learner for not knowing technical concepts.

The course should make each step feel controlled and verifiable.

## Scope boundaries

The course should cover:

- what ChatGPT does in the workflow;
- what Codex does in the workflow;
- why one task at a time matters;
- why documentation is source of truth;
- how GitHub preserves project history;
- why deploy keys must be handled safely;
- why private keys and secrets must not be printed;
- how to check that something really changed;
- how to read a Codex report;
- how to verify a public preview page;
- why `localhost` must not be shown as the learner-facing address;
- how agent and tool differ at a beginner level.

The course should not cover in the MVP:

- production security;
- complex backend architecture;
- payments;
- user accounts;
- advanced CI/CD;
- multiple agents running automatically;
- full LMS export;
- advanced model orchestration;
- OpenScript Agent Lab internals;
- APM/autopostmanager;
- OpenDesign Lab;
- legal, financial, medical, or safety-critical automation.

## Prerequisites

Before starting the course, the learner should have:

- access to ChatGPT;
- access to Codex or a Codex-like executor;
- a GitHub account;
- access to a server prepared by the operator or mentor;
- ability to copy and paste text;
- ability to upload markdown documents through UI.

The learner does not need to know how these systems work internally before the course begins.

## Source basis

Use the accepted Source Analyst output:

`source_digest.md`

The source digest is accepted as the first pipeline proof and has status:

`PASS_SOURCE_DIGEST_READY`

## Human decisions

For this first test, use the following decisions:

1. The first course is for absolute beginners.
2. The course should be practical, not theoretical.
3. The course should teach the workflow through one small project.
4. The MVP course should be 6 to 8 lessons.
5. The course must keep the proof-first, one-step-at-a-time method.
6. The course should not include advanced production architecture.
7. The course should carry source gaps forward instead of hiding them.

## Known source gaps to carry forward

Carry forward the gaps from `source_digest.md`, especially:

- full roadmap of the first project may be missing;
- full AGENTS.md for the working project may be missing;
- full prompt templates may be missing;
- technical specification may be missing;
- module map may be missing;
- current status may be missing;
- source/runtime boundary may be missing;
- vendor notes may be missing;
- examples of final Codex reports may be missing.

Do not pretend these gaps are solved.

Design around them where possible.

Stop only if a gap blocks the curriculum map.
