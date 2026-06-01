# Current status

Course Factory now has a local and public admin MVP.

The repository at `/opt/course-factory` remains pushed to the public GitHub repository.

Current stage:

Stage 2 — Admin MVP with Basic Auth and file-based agent/skill test bench.

The admin now also has a runs page that creates selected-agent run requests only.
The UI does not execute Codex or model calls.
The first intended test agent for the run workflow is Source Analyst.

No production backend or production deployment beyond this authenticated MVP has been approved yet.

The immediate priority is using the admin to edit markdown files in `skills/`, then creating controlled run requests for the file-based agent/skill test bench.
