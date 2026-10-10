# Granma Wasfiyya – Over the Shoulder (prototype)

2.5D pseudo-3D walking prototype (canvas, no engine). Open `index.html` in a browser.

- `index.html` – current build: video walk cycle + near/far slap (7.8 MB, self-contained, GitHub Pages ready). Built from `src/game.slap.src.html` with `tools/build_slap_game.py`.
- (the earlier screenshot-based version was removed to keep the zip small)
- `src/game.slap.src.html` (main), `src/game.video.src.html`, `src/game.src.html` – editable sources; `/*ASSETS*/` is replaced at build time.
- `assets/` – sliced props, paving, shadow, backdrop.
- `assets_video/` – 24 WebP walk frames + `meta.json`.
- `tools/` – build and asset scripts; all paths are repo-relative, intermediates go to git-ignored `work/`:
  - `python3 tools/build_slap_game.py` → `index.html` (the game). `build_video.py` → `index_video.html`, `build.py` → `index_screenshot_version.html` (older variants, not committed).
  - `slice.py` – props/paving/shadow/backdrop from `art/source/props_sheet.png` into `assets/`.
  - Walk cycle: `ffmpeg -i art/source/walk_video.mp4 work/video/raw/f_%03d.png`, then `runall.py` (uses `key.py`) and `export.py` → `assets_video/`.
  - Slap: frames of `art/source/slap_video.mp4` into `work/slap/raw/f_%03d.png`, then `gkey.py` and `build_slap.py` → `assets_slap/` (needs `work/video/walk_png` from the walk step).
  - `node tools/smoke.cjs [page.html]` – headless smoke test (JS errors + screenshots in `work/smoke/`).
  - Asset scripts need `opencv-python scipy pillow numpy`.
- `art/` – source sheet, source videos, raw cuts (the 24 video walk PNG frames can be regenerated with tools/export.py).

Controls: W/A/D or arrows, drag to look, Q/E camera angle, P pause, H hide help.
Note: AI-generated art; check the PixVerse terms before public/commercial use.

## Slap system (added)
- `assets_slap/` – `slapA_*.webp` (near, 32 frames) and `slapB_*.webp` (far, 35 frames), `meta_slap.json` (frame count, pivot, hit frame, 30 fps), `sfx_slapA/B.mp3` (cut from the Gemini video's audio, aligned to the strike frames).
- Source: `art/source/slap_video.mp4` (green screen). `tools/gkey.py` keys it; `tools/build_slap.py` retimes (long wind-ups sped up, strike at real speed), reshapes her to the original Mama's proportions (row-by-row width warp measured in `art/slap_prof/`), colour-matches and exports.
- In game: `slapAt({x,z})` picks near (<1.8 m) or far and mirrors the clip for enemies on the left. Keys: Space (alternate), J near, K far; hand button on screen.

Claude Code: `.claude/agents/` defines cheaper subagents (Haiku `mechanic`, Sonnet `implementer` / `verifier`); the main session plans and delegates — see `CLAUDE.md`.
Deploy: pushing to `Shoulder` publishes to GitHub Pages via `.github/workflows/pages.yml` (also runnable by hand / the `deploy` skill).

## License
© 2026 farpaci. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) — see `LICENSE`.
You may share and adapt it **non-commercially**, only with credit to *Granma Wasfiyya by farpaci* and a link to this repository, and only under the same license. Presenting it (or a modified version) as your own, or selling/marketing it, is not allowed.
