# Mama Wasfiyya – Over the Shoulder (prototype)

2.5D pseudo-3D walking prototype (canvas, no engine). Open `index.html` in a browser.

- `index.html` – current build: video walk cycle + near/far slap (7.8 MB, self-contained, GitHub Pages ready). Built from `src/game.slap.src.html` with `tools/build_slap_game.py`.
- (the earlier screenshot-based version was removed to keep the zip small)
- `src/game.video.src.html`, `src/game.src.html` – editable sources; `/*ASSETS*/` is replaced at build time.
- `assets/` – sliced props, paving, shadow, backdrop.
- `assets_video/` – 24 WebP walk frames + `meta.json`.
- `tools/` – build and asset-processing scripts. `build_video.py` / `build.py` are path-relative (run from repo root: `python3 tools/build_video.py` after moving them to the root, or adjust `root`). The other scripts still contain absolute `/home/claude/game/...` paths and must be adjusted before use.
- `art/` – source sheet, source videos, raw cuts (the 24 video walk PNG frames can be regenerated with tools/export.py).

Controls: W/A/D or arrows, drag to look, Q/E camera angle, P pause, H hide help.
Note: AI-generated art; check the PixVerse terms before public/commercial use.

## Slap system (added)
- `assets_slap/` – `slapA_*.webp` (near, 32 frames) and `slapB_*.webp` (far, 35 frames), `meta_slap.json` (frame count, pivot, hit frame, 30 fps), `sfx_slapA/B.mp3` (cut from the Gemini video's audio, aligned to the strike frames).
- Source: `art/source/slap_video.mp4` (green screen). `tools/gkey.py` keys it; `tools/build_slap.py` retimes (long wind-ups sped up, strike at real speed), reshapes her to the original Mama's proportions (row-by-row width warp measured in `art/slap_prof/`), colour-matches and exports.
- In game: `slapAt({x,z})` picks near (<1.8 m) or far and mirrors the clip for enemies on the left. Keys: Space (alternate), J near, K far; hand button on screen.
