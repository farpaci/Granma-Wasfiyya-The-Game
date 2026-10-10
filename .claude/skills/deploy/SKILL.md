---
name: deploy
description: Deploy the game to GitHub Pages (https://farpaci.github.io/Mama-lulwa-game/) from the Shoulder branch, and watch the run until it succeeds or fails. Use when the user asks to deploy, publish, release, or "push it live".
---
# Deploy to GitHub Pages

Workflow: `.github/workflows/pages.yml` ("Deploy to GitHub Pages"). It rebuilds `index.html` from `src/game.slap.src.html` and deploys it. Every push to `Shoulder` deploys automatically; this skill is for deploying on demand or checking a deploy.

1. **Make sure `Shoulder` has the change.** `git fetch origin Shoulder && git log -1 --oneline origin/Shoulder`. Unpushed work must be committed and pushed first (delegate to the `mechanic` subagent per CLAUDE.md). If that push just happened, it already started a deploy — skip to step 3 instead of triggering a second one.
2. **Trigger** with the GitHub MCP tool (load via ToolSearch `select:mcp__github__actions_run_trigger,mcp__github__actions_list,mcp__github__actions_get,mcp__github__get_job_logs` if needed):
   `mcp__github__actions_run_trigger` → `method: run_workflow`, `owner: farpaci`, `repo: Mama-lulwa-game`, `workflow_id: pages.yml`, `ref: Shoulder`.
3. **Find the run**: `mcp__github__actions_list` → `method: list_workflow_runs`, `resource_id: pages.yml`, `workflow_runs_filter: {branch: Shoulder}`, `perPage: 3`. Take the newest run id.
4. **Watch**: `mcp__github__actions_get` → `method: get_workflow_run`, `resource_id: <run id>`. A run takes ~1 min; wait with a Monitor/until-loop or ScheduleWakeup, not a foreground sleep. Check again until `status: completed`.
5. **Report**: on `conclusion: success`, give the URL https://farpaci.github.io/Mama-lulwa-game/. On failure, `mcp__github__get_job_logs` with `run_id`, `failed_only: true`, `return_content: true`, `tail_lines: 80`, and explain the cause.

Known failure: `Branch "Shoulder" is not allowed to deploy to github-pages due to environment protection rules` → the user must add `Shoulder` under repo Settings → Environments → github-pages → Deployment branches and tags. This cannot be fixed from code.
