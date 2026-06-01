# AGENTS.md

## Project

Course Factory.

## Current rule

This repository is in bootstrap stage.

Do not build backend, UI, runtime services, or production deployment until the agent/skill test bench is proven.

## Safety

Do not read or commit secrets.

Do not commit runtime state, logs, databases, credentials, private keys, auth files, `.env` files, or tokens.

Do not copy documents from other projects until they are reviewed for relevance and public-safety.

## Workflow

One run = one task.

Proof first, then design, then minimal change, then repeat proof.

All changes must be git-tracked.

## Course content rule

Course and lesson content must be source-grounded.

Agents must not invent facts that are not present in provided source materials unless explicitly marked as instructional inference.

## Local admin MVP

The admin server must bind only to `127.0.0.1:8091`.

Editable scope is limited to markdown files under `skills/`.

Do not allow arbitrary file paths, symlink escapes, or hidden files.

Saving changes updates the file locally only. Commit and push are separate Codex runs.
