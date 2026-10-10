# Project notes
Single-file canvas game. Edit `src/*.src.html`, then rebuild into `index.html` (inlines assets as data URIs).
Ground is rendered per pixel in JS (perf risk on old phones: lower `g.w` in `resize()`).
Walk cycle: `META` (frames, pivot, idle) comes from `assets_video/meta.json`; phase advances 24 frames per 2.4 m.
Known gaps: no shopfront facades along the street, no turning frames, olive specks near feet in a few video frames.
Rebuild: `python3 tools/build_video.py` (index.html) / `python3 tools/build.py` (index_screenshot_version.html). Tool paths are repo-relative; intermediates go to git-ignored `work/`.
Smoke test: `node tools/smoke.cjs [page.html]` — headless Chromium, walks forward, fails on JS errors, screenshots to `work/smoke/`.
Never Read `index.html` / `index_screenshot_version.html` directly (multi-MB inlined assets).

# Model division of labor
The main session (Opus) is the lead: it talks to the user, reads just enough code to plan, writes the plan, and reviews results. Commit/push is delegated too. It delegates execution to subagents in `.claude/agents/`:
- `mechanic` (Haiku): mechanical chores — rebuilds, smoke runs, grep/fact-finding, find/replace, renames, and git commit/push with the message the lead gives.
- `implementer` (Sonnet): writes the code for a decided plan, rebuilds, runs smoke.
- `verifier` (Sonnet): reviews the diff + screenshots against the goal; PASS/FAIL.
Flow: plan (lead) → implementer → verifier → lead reviews the report → mechanic commits and pushes. Give subagents self-contained prompts (files, functions, behavior, acceptance checks); they do not see this conversation. Do it inline only when the task is a one-line edit or delegating would cost more than doing it.
