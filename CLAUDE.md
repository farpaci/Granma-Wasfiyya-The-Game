# Project notes
Single-file canvas game. Edit `src/*.src.html`, then rebuild into `index.html` (inlines assets as data URIs).
Ground is rendered per pixel in JS (perf risk on old phones: lower `g.w` in `resize()`).
Walk cycle: `META` (frames, pivot, idle) comes from `assets_video/meta.json`; phase advances 24 frames per 2.4 m.
Known gaps: no shopfront facades along the street, no turning frames, olive specks near feet in a few video frames.
Scripts in `tools/` have hardcoded absolute paths from the original sandbox; fix before running.

Slap: `slapAt(enemy)` in the source is the hook for the enemy system. Slap clips are right-handed; left is the same clip drawn mirrored around the body-centre pivot (`META_SLAP[k].pivot`). Hit frame (`META_SLAP[k].hit`) triggers sound, shake and the SLAP! pop; slap frames decode lazily after the core art. Scripts in tools/ still use absolute sandbox paths.
