# Combo pose sources

One 16:9 sheet per man, five figures left to right: neutral, hit1 (holds right cheek), hit2 (dodge lean), fall (kicked), down (lying).
Granma is on the man's right (screen-left); the game mirrors sprites for the other side.

| file | notes |
|---|---|
| `man_tank_sheet.webp` | 1024x572. Figure 3 (dodge) leans TOWARDS granma (screen-left): mirror it when cutting. Cap is backwards in 1, 2, 5 and forward in 3, 4 (accepted). Shoes are all red (walk loop has white-red). |
| `man_thobe_ref.jpg` | 1342x2000, neutral reference. |
| `man_thobe_hit1.jpg` | Holds his LEFT cheek (screen-right): mirror it when cutting. |
| `man_thobe_hit2_BROKEN.jpg` | Has a second floating head (top left): not usable, waiting for a regenerated version. Lean direction (screen-right) is correct. |
| `man_thobe_fall.jpg` | Falls towards screen-right, correct. Tilt is ~30° (game can add rotation). |
| `man_thobe_down.jpg` | Landscape, feet towards camera, correct. |
