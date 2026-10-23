# Art brief: 3-hit combo (slap · slap · kick) and new men

> **Don't paste this file into Gemini.** Use `prompt-cards.html` (published at https://claude.ai/artifact/EESZ4NFQtsUN2sko5AuCQH): one self-contained prompt per image with a copy button. Regenerate it with `python3 tools/briefs/prompt_page.py . art/briefs/prompt-cards.html`; the reference sheets come from `python3 tools/briefs/ref_sheets.py .`.

Gameplay this art is for:
1. **1st slap** → the man stops and **holds his slapped cheek**.
2. **2nd slap** → he **leans ~45° sideways away from Granma** to dodge a third slap.
3. Granma **kicks** him instead → he **falls to the ground** and fades out.

Reference sheets are in `refs/` (green background, same as the game's pipeline):
- `refs/granma_back_view.png`: Granma from behind, walking, and both slap poses.
- `refs/man_<id>.png`: each man in two walk frames (left, the in-game outfit) and his hands-up photo (right, sharper face detail). Ids: `thobe`, `tank`, `tee`, `hoodie`, `shirt`, `shemagh`.

The walk frames are small and slightly blurry, so give Gemini **both** parts of the sheet. **Outfit:** follow the walk frames, because that's what the player sees. For example, `tank` wears a red cap and dark charcoal joggers while walking. **Face:** follow the photo.

## Direction convention (important)
All men face the camera. Draw every man pose with **Granma on HIS RIGHT side (screen-left)**. The game mirrors the sprite when he is on her other side.
- He holds his **right** cheek (on the screen-left side of the image).
- He leans to **his left** (screen-right), away from her.
- The kick hits his **right hip/thigh**, so he falls toward **his left** (screen-right).

Draw Granma, seen from behind, kicking **to her right (screen-right)**. The game mirrors it for the left side.

## Rules for every image (so the game's keyer can cut them out)
Paste this block at the end of every prompt:

```
Technical requirements: single character only, full body from head to shoes with empty margin around, centered. Background: perfectly flat solid chroma-key green (#00B140), no gradient, no floor, no cast shadow, no props. Character wears no green. Photorealistic, same soft frontal studio lighting and colour grading as the reference image, sharp focus, no motion blur. Portrait orientation 2:3, at least 1024 px tall. No text, no logo, no watermark, no border.
```

Make **one image per request** (not three people in one image). Keep the same seed or conversation in Gemini so the character stays consistent.

---

## A. Existing six men: 4 images each

Attach `refs/man_<id>.png` and start each prompt with:
`Use the attached reference: same man, same face, same hair/beard, same outfit as the two walking frames on the left (use the photo on the right only for face detail). Front view facing the camera, camera at chest height.`

**A1 · Hit 1, holding the cheek**
```
He has just been slapped hard on his RIGHT cheek. He stands with feet planted, head turned slightly to his left, eyes squeezed, mouth open in a pained "ouch", his RIGHT hand pressed flat against his right cheek, left arm half raised in shock. Comic but realistic expression.
```

**A2 · Hit 2, leaning away to dodge**
```
After a second slap he leans his whole upper body about 45 degrees to HIS LEFT (towards the right side of the image), bending sideways at the waist, feet still planted shoulder-width apart, both forearms raised in front of his face defensively, flinching, one eye peeking out, frightened and pleading.
```

**A3 · Kicked, falling (mid-air)**
```
He has been kicked on his RIGHT hip and is falling sideways to HIS LEFT (towards the right side of the image): body tilted about 60 degrees, right leg lifted off the ground, arms flailing outward, face shocked with mouth wide open. Only his left foot still touches the ground.
```

**A4 · Lying on the ground**
```
He lies flat on his back on the ground after falling, dazed, seen from the front and slightly above (camera at standing eye level, 2 metres in front of his feet), feet towards the camera, head away from the camera, arms spread out, eyes closed or dizzy. The whole body fits in the frame with margin.
```
For A4, use **landscape 3:2** instead of 2:3.

---

## B. Granma's kick (from behind)

You can make the kick in two ways. **A video is better** (smooth motion, the same pipeline as the slap clip); the stills are a fallback.

**B-video (Gemini/Veo video, ~3 s, green screen):** attach `refs/granma_back_view.png` (first figure) as the first frame.
```
Rear view of the same elderly woman as the reference (black headscarf, brown patterned cardigan, red floral skirt, grey trousers, beige socks, burgundy shoes), seen from directly behind at chest height on a flat chroma-key green background (#00B140). She stands still, shifts her weight onto her left leg, then delivers one strong sideways kick with her RIGHT leg out to her right side at hip height, skirt swinging, arms out for balance, holds the kick for a moment, then puts the foot back down and returns to standing. Camera completely static, full body always in frame with margin, no cast shadow, no other people, no text.
```

**B-stills (if no video):** attach the same reference, prefix with `Same elderly woman as the reference, seen from directly behind at chest height:` and generate:
- **B1 wind-up:** `weight on her left leg, right knee lifted and chambered towards her body, arms out for balance, leaning slightly to her left.`
- **B2 kick:** `RIGHT leg fully extended sideways to her right at hip height, sole of the shoe pointing right, torso leaning to her left, skirt flaring, arms out.`
- **B3 recover:** `right foot coming back down next to the left, body straightening, arms lowering.`

---

## C. New men

Each new man needs:
1. **A base image** (prompt below): front view, standing neutrally, arms relaxed.
2. **A walk video:** feed the base image to **Viggle** with a "walk towards camera" template on a green background, as for the current six. Use the paid plan without a watermark if possible; the current walk video has the free-tier watermark.
3. **A1–A4** above, using his base image as the reference.

Base prompt template:
```
Full-body photo of [DESCRIPTION], standing upright facing the camera, arms relaxed at his sides, neutral slightly cocky expression, camera at chest height.
```
Add the technical-requirements block at the end.

Suggested new characters (distinct silhouettes and colours, no green clothing):

| id | [DESCRIPTION] |
|---|---|
| `tourist` | a sunburnt middle-aged European tourist in a wide straw hat, loud orange Hawaiian shirt, beige cargo shorts, white socks with sandals, big camera around his neck |
| `courier` | a young delivery rider in a blue-and-white jacket, open motorcycle helmet, square insulated delivery backpack, black trousers, sneakers |
| `suit` | a slick businessman in a tight navy suit, open white collar, slicked-back hair, sunglasses on his head, phone in one hand, pointed brown shoes |
| `influencer` | a man in his early thirties with a trimmed beard and styled hair, a social-media influencer in a bright purple bomber jacket over a white T-shirt, light ripped jeans, chunky white sneakers, holding a phone on a selfie stick |
| `fisher` | a stocky fisherman in a yellow waterproof apron over a striped shirt, rolled-up sleeves, black rubber boots, woollen cap |
| `uncle` | a big-bellied older man with a grey moustache in a white vest and loose brown sirwal trousers, plastic slippers, prayer beads in his hand |

---

## Delivery
- Name files like `man_<id>_hit1.png`, `_hit2.png`, `_fall.png`, `_down.png`, `granma_kick.mp4` (or `granma_kick_1..3.png`), `man_<id>_base.png` + `man_<id>_walk.mp4`.
- Upload them to the chat, or put them in `art/source/combo/`.
- The pipeline cuts them out, scales them to each man's height and wires up the 3-hit logic.
