# Combo pose sources

One 16:9 sheet per man, five figures left to right: neutral, hit1 (holds right cheek), hit2 (dodge lean), fall (kicked), down (lying).
Granma is on the man's right (screen-left); the game mirrors sprites for the other side.

| file | notes |
|---|---|
| `man_tank_sheet.jpg` | 2000x1116 high-res version (replaces the 1024 px webp). Figure 3 (dodge) leans TOWARDS granma (screen-left): mirror it when cutting. Cap backwards in 1, 2, forward in 3, 4, 5 (accepted). Shoes all red (walk loop has white-red). |
| `man_thobe_ref.jpg` | 1342x2000, neutral reference. |
| `man_thobe_hit1.jpg` | Holds his LEFT cheek (screen-right): mirror it when cutting. |
| `man_thobe_hit2_BROKEN.jpg` | Has a second floating head (top left): not usable, waiting for a regenerated version. Lean direction (screen-right) is correct. |
| `man_thobe_fall.jpg` | Falls towards screen-right, correct. Tilt is ~30° (game can add rotation). |
| `man_thobe_down.jpg` | Landscape, feet towards camera, correct. |
| `man_tee_sheet.jpg` | 2000x1116. 1, 2, 4 correct. Dodge (3) barely leans (~10°): add in-game rotation away from Granma. Down (5) lies head towards the camera (accepted). Figure 5's shoe is close to figure 4's standing foot but not touching. |
| `man_shirt_sheet.jpg` | 2000x1116. 1, 2, 4, 5 correct. Dodge (3) leans TOWARDS granma (~20°): mirror it and add rotation. |

| `man_shemagh_sheet.jpg` | 2000x1116, all five figures separate. 1, 2, 4, 5 correct. Dodge (3) leans slightly TOWARDS granma: mirror it and add rotation. |
| `granma_kick_sheet.jpg` | 2000x1116, back view, three separate figures: wind-up, kick (right leg out to the right at knee-hip height), recover. Scale to the walk sprite by body height. The Gemini video attempt (balancing, arms spread) was rejected. |
| `man_tourist_base.jpg` | New man `tourist`, 2000x1116 neutral reference. |
| `man_tourist_walk.mp4` | Gemini video 1280x720, 10 s. Only ~0-3.5 s is a clean walk towards the camera at constant size; afterwards he lifts the camera and walks into a close-up (feet cut). Cut the walk loop from the first part. |
| `man_tourist_sheet.jpg` | 2000x1116. 1, 2 correct. Dodge (3) leans towards granma: mirror. Figures 3, 4 and 5 form ONE blob (4's standing foot touches 5's feet, 3's hand near 4's leg): split with hand-drawn cut lines. Down (5) lies sideways, head to the right (accepted). |
**Touching figures:** in `man_tank_sheet` (figures 3+4), `man_tee_sheet` (4+5) and `man_shirt_sheet` (3+4) the kicked figure's raised leg touches its neighbour, so they form one connected blob. Split at the narrowest joining column when cutting (contact is only a shoe/hem).
