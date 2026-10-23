# Project notes
Single-file canvas game "Granma Wasfiyya". Main game: `src/game.slap.src.html` → `python3 tools/build_slap_game.py` → `index.html` (inlines assets as data URIs). `src/game.video.src.html` (walk only, → git-ignored `index_video.html`) and `src/game.src.html` (screenshot frames, → git-ignored `index_screenshot_version.html`) are older variants; port shared changes to the slap source first.
Ground is rendered per pixel in JS (perf risk on old phones: lower `g.w` in `resize()`).
Walk cycle: `META` (frames, pivot, idle) comes from `assets_video/meta.json`; phase advances 24 frames per 2.4 m.
Slap: `slapAt(enemy)` in the source is the hook for the enemy system. Slap clips are right-handed; left is the same clip drawn mirrored around the body-centre pivot (`META_SLAP[k].pivot`). Hit frame (`META_SLAP[k].hit`) triggers sound, shake and the SLAP! pop; slap frames decode lazily after the core art.
Enemies: five men (the hoodie man was removed and is being remade; `tools/build_enemies.py` would still re-create his old sprites from the video, so delete them after a rebuild) (`assets_enemy/`, built by `tools/build_enemies.py` from `art/source/enemies_walk.mp4` + `enemies_frozen_*.jpg`; `META_ENEMY`). Max 6 alive; spawn 55-70 m ahead in lanes at her slap reach (`_slapHand[clip].x_m`), walk toward her at 1.25 m/s; Space/hand button `slapAuto` targets the nearest eligible man via `slapEnemy`, who is lerped so her hand meets his face at the hit frame, then becomes `frozen` (hands-up still) in place; removed once behind the camera. HUD counts SLAPS.
Facades: procedural shopfronts at x=±FACADE_X (17.5 m), per-chunk `items.facades`, textures painted lazily (1/frame) in `facadeTex`, drawn as perspective strips in `drawFacades` (~3 ms/frame). Buildings have a depth `d` and draw a shaded end wall (`endTex`, one drawImage) at z1 unless `touchPrev`; drawn far->near. ~35% of chunks reserve a 14-26 m sea opening on one side (`open` entry) with a tiled stone balustrade (`balTex`) instead of a wall.
Known gaps: no turning frames, olive specks near feet in a few video frames.
Tool paths are repo-relative; intermediates go to git-ignored `work/` (`work/video`, `work/slap`, `work/shots`).
Smoke test: `node tools/smoke.cjs [page.html]` — headless Chromium, walks forward, fails on JS errors, screenshots to `work/smoke/`.
Never Read the generated `index*.html` files directly (multi-MB inlined assets).

# Branch and deploy
Work happens on `Shoulder`; every push to it deploys to GitHub Pages (`.github/workflows/pages.yml` rebuilds `index.html` from the slap source). Several sessions (Claude Code, claude.ai in the browser) push here: ALWAYS `git fetch origin Shoulder` and build on top of `origin/Shoulder` before changing anything, and never replace the tree wholesale from an uploaded zip — merge the zip's changes into the current files instead, keeping `.claude/`, `tools/smoke.cjs`, the workflow and this file.

# Model division of labor
The main session (Opus) is the lead: it talks to the user, reads just enough code to plan, writes the plan, and reviews results. Commit/push is delegated too. It delegates execution to subagents in `.claude/agents/`:
- `mechanic` (Haiku): mechanical chores — rebuilds, smoke runs, grep/fact-finding, find/replace, renames, and git commit/push with the message the lead gives.
- `implementer` (Sonnet): writes the code for a decided plan, rebuilds, runs smoke.
- `verifier` (Sonnet): reviews the diff + screenshots against the goal; PASS/FAIL.
Flow: plan (lead) → implementer → verifier → lead reviews the report → mechanic commits and pushes. Give subagents self-contained prompts (files, functions, behavior, acceptance checks); they do not see this conversation. Do it inline only when the task is a one-line edit or delegating would cost more than doing it.
