# Combo pose sources

One 16:9 sheet per man, five figures left to right: neutral, hit1 (holds right cheek), hit2 (dodge lean), fall (kicked), down (lying).
Granma is on the man's right (screen-left); the game mirrors sprites for the other side.

| file | notes |
|---|---|
| `man_tank_sheet.jpg` | 2000x1116 high-res version (replaces the 1024 px webp). Figure 3 (dodge) leans TOWARDS granma (screen-left): mirror it when cutting. Cap backwards in 1, 2, forward in 3, 4, 5 (accepted). Shoes all red (walk loop has white-red). |
| `man_tee_sheet.jpg` | 2000x1116. 1, 2, 4 correct. Dodge (3) barely leans (~10°): add in-game rotation away from Granma. Down (5) lies head towards the camera (accepted). Figure 5's shoe is close to figure 4's standing foot but not touching. |
| `man_shirt_sheet.jpg` | 2000x1116. 1, 2, 4, 5 correct. Dodge (3) leans TOWARDS granma (~20°): mirror it and add rotation. |

| `man_shemagh_sheet.jpg` | 2000x1116, all five figures separate. 1, 2, 4, 5 correct. Dodge (3) leans slightly TOWARDS granma: mirror it and add rotation. |
| `granma_kick_sheet.jpg` | 2000x1116, back view, three separate figures: wind-up, kick (right leg out to the right at knee-hip height), recover. Scale to the walk sprite by body height. The Gemini video attempt (balancing, arms spread) was rejected. |
| `man_tourist_base.jpg` | New man `tourist`, 2000x1116 neutral reference. |
| `man_tourist_walk.mp4` | Gemini video 1280x720, 10 s. Only ~0-3.5 s is a clean walk towards the camera at constant size; afterwards he lifts the camera and walks into a close-up (feet cut). Cut the walk loop from the first part. |
| `man_tourist_sheet.jpg` | 2000x1116. 1, 2 correct. Dodge (3) leans towards granma: mirror. Figures 3, 4 and 5 form ONE blob (4's standing foot touches 5's feet, 3's hand near 4's leg): split with hand-drawn cut lines. Down (5) lies sideways, head to the right (accepted). |
| `man_suit_base.jpg` | New man `suit`, 2000x1116 neutral reference. |
| `man_suit_sheet.jpg` | 2000x1116, all five figures separate. 1, 2, 4, 5 correct. Dodge (3) leans towards granma: mirror. |
| `man_suit_walk_sheet.webp` | ChatGPT, 1536x1024 RGBA with a TRANSPARENT background (already cut out; use alpha, no keying). 8 separate frames ~465 px tall, 2 rows of 4. Row 2 is close to row 1; build the loop from whichever frames alternate the feet cleanly. |
| `man_courier_base.webp` | New man `courier`, 1024x1536 neutral reference. |
| `man_courier_sheet.webp` | 1672x941, all five figures separate. 1, 2, 4, 5 correct. Dodge (3) leans towards granma: mirror. |
| `man_courier_walk_sheet.webp` | ChatGPT 1536x1024, green background, 8 separate frames ~470 px, 2 rows of 4. |
| `man_influencer_base.webp` | New man `influencer`, 1024x1536, holds a phone on a selfie stick. |
| `man_influencer_sheet.webp` | 1672x941, all five figures separate. No selfie stick in any pose (reads as the phone being knocked away on the first slap; accepted). Hit1 (2) holds his LEFT cheek and dodge (3) leans towards granma: mirror both. 4, 5 correct. |
| `man_influencer_walk_sheet.webp` | ChatGPT 1536x1024, green background, 8 separate frames ~465 px, selfie stick raised in all frames. |
| `man_uncle_base.jpg` | New man `uncle`, 2000x1116 neutral reference (prayer beads in his left hand). |
| `man_uncle_sheet.webp` | 1672x941, all five figures separate and all directions correct (dodge leans away from granma), no mirroring needed. |
| `man_uncle_walk_sheet.webp` | ChatGPT 1536x1024 RGBA, TRANSPARENT background (use alpha, no keying). 8 separate frames ~455 px. Prayer beads missing in two frames (accepted). |
| `man_thobe_sheet.webp` | Remade thobe man (replaces all earlier thobe images and his in-game walk/frozen sprites). 1672x941 RGBA, TRANSPARENT background, five separate figures. 1, 2, 4, 5 correct; dodge (3) leans towards granma: mirror. |
| `man_thobe_walk_sheet.webp` | ChatGPT 1536x1024 RGBA, TRANSPARENT background, 8 separate frames ~460 px. |
| `man_hoodie_base.webp` | Remade hoodie man (new face, replaces the removed one), 1024x1536. |
| `man_hoodie_sheet.webp` | 1672x941, five separate figures. 1, 2, 4, 5 correct; dodge (3) leans towards granma: mirror. |
| `man_hoodie_walk_sheet.webp` | ChatGPT 1536x1024, green background, 8 separate frames ~470 px. |
**Touching figures:** in `man_tank_sheet` (figures 3+4), `man_tee_sheet` (4+5) and `man_shirt_sheet` (3+4) the kicked figure's raised leg touches its neighbour, so they form one connected blob. Split at the narrowest joining column when cutting (contact is only a shoe/hem).

## Tea-table groups (table-kick feature)
Three alternative actions, picked at random per group. Seen from the street; Granma kicks from the LEFT (canonical: group on her right, screen-right); mirror for the other side.

| file | notes |
|---|---|
| `group_adana_a_run_sheet.webp` | 1536x1024 green, 3+2 panels: calm, kick impact, jumping up (table already on the ground), men running (men ONLY, no table), aftermath (table/stools/glasses only). Panel 3 touches the right edge (a hand may be clipped). |
| `group_adana_a_stay_sheet.webp` | 2000x719 RGBA transparent, same group A, 3 panels: calm, kick impact, aftermath where the men stay standing and shouting (one sits on the ground) next to the overturned table. Panel 3 touches the right edge. |
| `group_adana_b_run_sheet.webp` | 1536x1024 green, group B (3 men), same 5 moments as the A run sheet; in panel 4 the three runners are separate blobs. |

Cutting notes: register all panels of a sheet on the TABLE (its base / the stools' footprint) so the scene doesn't jump between frames; the "men running" panel has no table, so in game draw the aftermath panel (table) underneath it and move the runners away from the table while they fade.
