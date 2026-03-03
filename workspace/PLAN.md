# PLAN.md

This file is the canonical project plan and orchestration register for the workspace.

Conventions
- Roles (convention only):
  - Manager: github-copilot/gpt-5-mini — preferred planner (convention)
  - Logic/Debug: github-copilot/gpt-4.1 — debugging and reasoning (convention)
  - Features: github-copilot/gpt-4o — implementation & general tasks (convention)
- Status values: Backlog / In Progress / Waiting / Review / Done / Blocked
- When a long-running task is started, mark it In Progress here and add a brief note.
- This file is updated by the assistant when tasks start/stop and when you request changes.

Project metadata
- Owner: Ken
- Assistant: Yuetki
- Created: 2026-03-02

Current tasks

1) Build: News briefing DOCX (bilingual)
- ID: TASK-003
- Status: Done
- Owner: Yuetki
- Started: 2026-03-02 15:33 (HK)
- Completed: 2026-03-02 19:26 (HK)
- Description: Produce bilingual (English + Chinese) news briefing DOCX with top headlines (Worldwide / US / Hong Kong) and market section (US stocks & options top 5 each). Update with live tickers/options and upload to group.
- Artifact:
  - C:\Users\n1sol\.openclaw\workspace\briefing_final_20260302_192609.docx
- Notes: Completed run using parallel fetch + aggregation. Sources: CNBC, Yahoo Finance, Benzinga, MarketWatch, Seeking Alpha; Bloomberg/WSJ used for headlines where available (paywall fallbacks noted). Uploaded to Telegram group.
- Next action: Await user review or requests for revision (format, additional tickers, PDF export, logo).

2) Policy/Orchestration convention
- ID: TASK-002
- Status: Backlog
- Owner: Ken / Yuetki
- Description: Adopt orchestration roles and use PLAN.md as canonical plan file. Assistant will not change model usage or enforce runtime policies; roles listed are a naming convention for planning.

3) Task billing convention
- ID: POLICY-001
- Status: Active
- Owner: Ken / Yuetki
- Description: By default, each new user-assigned task will consume at most one model request. The assistant will perform non-model actions (monitoring, CLI checks, log collection, rule-based detection) as needed during the task without calling the language model. At task completion (or when the user explicitly asks), the assistant will issue a single model request to produce summaries/translations/reports.
- Exceptions: The user may explicitly pre-authorise additional model requests for a task (e.g., continuous summaries, bilingual separate passes, or multi-step planning). Any exception will be recorded in PLAN.md before execution.

Scheduled tasks (requested by user)
- DAILY-OUTSTANDING
- Action: Send a simple list of outstanding tasks from PLAN.md to the Telegram group at 08:30 HK local time daily.
- Enabled: Yes (per user confirmation)

- BRIEFING-SCHEDULE
- Action: Fetch news & market briefing, build bilingual DOCX and post to Telegram group.
- Times (HK): 07:00, 13:00, 18:00 daily
- Enabled: Yes (per user confirmation)

PR/Branches
- No branches created yet. When code work begins, Assistant will prepare branch name suggestions and PR text and add them here.

How to use this file
- Ask the assistant to "update PLAN.md" or request status; assistant will edit this file and report the diff.
- To mark a task Done or change status, ask explicitly (e.g., "mark TASK-003 Done").

Change log
- 2026-03-02 14:31 — PLAN.md created; TASK-001 added and marked In Progress (Yuetki).
- 2026-03-02 17:08 — TASK-001 polling terminated per user request.
- 2026-03-02 18:20 — TASK-001 removed; TASK-003 marked In Progress per user request.
- 2026-03-02 18:49 — TASK-004 removed and POLICY-001 (one-request-per-task) added per user instruction.
- 2026-03-02 19:26 — TASK-003 completed; briefing_final_20260302_192609.docx created and uploaded to group.
