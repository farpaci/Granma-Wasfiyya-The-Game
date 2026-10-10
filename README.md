# Mama Lulwa – Over the Shoulder (prototype)

2.5D pseudo-3D walking prototype (canvas, no engine). Open `index.html` in a browser.

- `index.html` – video-driven walk cycle (24 frames from the PixVerse clip). Self-contained, GitHub Pages ready.
- `index_screenshot_version.html` – earlier version using 8 frames cut from screenshots.
- `src/game.video.src.html`, `src/game.src.html` – editable sources; `/*ASSETS*/` is replaced at build time.
- `assets/` – sliced props, paving, shadow, backdrop (+ screenshot-based `mama1-8.png`).
- `assets_video/` – 24 WebP walk frames + `meta.json`.
- `tools/` – build and asset-processing scripts. `build_video.py` / `build.py` are path-relative (run from repo root: `python3 tools/build_video.py` after moving them to the root, or adjust `root`). The other scripts still contain absolute `/home/claude/game/...` paths and must be adjusted before use.
- `art/` – source sheet, source video, raw cuts.

Controls: W/A/D or arrows, drag to look, Q/E camera angle, P pause, H hide help.
Note: AI-generated art; check the PixVerse terms before public/commercial use.
