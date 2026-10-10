# Mama Lulwa – Over the Shoulder (prototype)

2.5D pseudo-3D walking prototype (canvas, no engine). Open `index.html` in a browser.

- `index.html` – video-driven walk cycle (24 frames from the PixVerse clip). Self-contained, GitHub Pages ready.
- `index_screenshot_version.html` – earlier version using 8 frames cut from screenshots.
- `src/game.video.src.html`, `src/game.src.html` – editable sources; `/*ASSETS*/` is replaced at build time.
- `assets/` – sliced props, paving, shadow, backdrop (+ screenshot-based `mama1-8.png`).
- `assets_video/` – 24 WebP walk frames + `meta.json`.
- `tools/` – build and asset-processing scripts. All paths are relative to the repo root, so they run from any directory:
  - `python3 tools/build_video.py` → `index.html`; `python3 tools/build.py` → `index_screenshot_version.html`.
  - `slice.py` – cuts props/paving/shadow/backdrop from `art/source/props_sheet.png` into `assets/`.
  - Video walk cycle: `ffmpeg -i art/source/walk_video.mp4 work/video/raw/f_%03d.png` (make the dir first), then `runall.py` (keys frames via `key.py`) and `export.py` → `assets_video/`.
  - Screenshot frames: `cut2.py` → `cut3.py` → `mama_frames.py`, working in `work/shots/` (needs the original screenshots `s0-5.png`, not in the repo).
  - `node tools/smoke.cjs [page.html]` – headless smoke test (JS errors + screenshots in `work/smoke/`).
  - Asset scripts need `opencv-python scipy pillow numpy`. `work/` is scratch space and git-ignored.
- `art/` – source sheet, source video, raw cuts.

Controls: W/A/D or arrows, drag to look, Q/E camera angle, P pause, H hide help.
Note: AI-generated art; check the PixVerse terms before public/commercial use.

Claude Code: `.claude/agents/` defines cheaper subagents (Haiku `mechanic`, Sonnet `implementer` / `verifier`); the main session plans and delegates — see `CLAUDE.md`.
Deploy: pushing to `Shoulder` publishes to GitHub Pages via `.github/workflows/pages.yml` (also runnable by hand / the `deploy` skill).
