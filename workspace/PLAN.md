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

1) Monitor: Croucher Science Week events page
- ID: TASK-001
- Status: In Progress
- Owner: Yuetki
- Started: 2026-03-02 14:25 (HK)
- Description: Poll https://croucherscienceweek.hk/hk/events every 30s until event listings or an "Apply" link appears. When an apply option is detected, stop polling and report available events and apply options to Ken for decision.
- Notes: Polling initiated per user instruction. Assistant has loaded site via attached browser; page currently returns 500 / 504 (server error). Screenshot saved to workspace media.
- Next action: Continue polling every 30s and report immediately when content appears.

2) Policy/Orchestration convention
- ID: TASK-002
- Status: Backlog
- Owner: Ken / Yuetki
- Description: Adopt orchestration roles and use PLAN.md as canonical plan file. Assistant will not change model usage or enforce runtime policies; roles listed are a naming convention for planning.

PR/Branches
- No branches created yet. When code work begins, Assistant will prepare branch name suggestions and PR text and add them here.

How to use this file
- Ask the assistant to "update PLAN.md" or request status; assistant will edit this file and report the diff.
- To mark a task Done or change status, ask explicitly (e.g., "mark TASK-001 Done").

Change log
- 2026-03-02 14:31 — PLAN.md created; TASK-001 added and marked In Progress (Yuetki). Requested orchestration convention recorded.
