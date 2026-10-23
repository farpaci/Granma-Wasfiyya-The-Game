import base64, io, html, json, os, sys
from PIL import Image
R, OUT = sys.argv[1], sys.argv[2]
REF = os.path.join(R, 'art', 'briefs', 'refs')
def thumb(name, w=900):
    im = Image.open(os.path.join(REF, name)).convert('RGB')
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=72); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
def tech(orient='portrait 2:3'):
    return ("Technical requirements: generate exactly ONE image showing exactly ONE person. Full body from head to shoes with empty margin around, centered. "
            "Background: perfectly flat solid chroma-key green (#00B140), no gradient, no floor, no cast shadow, no props. The person wears nothing green. "
            "Photorealistic, soft frontal studio lighting, sharp focus, no motion blur. Orientation " + orient + ", at least 1024 px tall. No text, no logo, no watermark, no border.")
MEN = [
 ('thobe', 'Beyaz thobe', 'a bearded Gulf Arab man in a long white thobe (dishdasha), white ghutra headscarf held by a black agal, brown leather sandals'),
 ('tank', 'Kırmızı atlet', 'a muscular bearded man in a red sleeveless tank top, a red baseball cap, dark charcoal jogger pants with white drawstrings, white sneakers with red accents'),
 ('tee', 'Siyah tişört', 'a bald, heavily built man with a full dark beard and tattooed forearms, in a tight black T-shirt, blue jeans and white sneakers'),
 ('hoodie', 'Kırmızı kapüşonlu', 'a young man with curly black hair and stubble, in a red zip-up hoodie over a white T-shirt, royal-blue track pants and white sneakers'),
 ('shirt', 'Mavi gömlek', 'a bearded man wearing a white knitted kufi cap, a light-blue button-up shirt with rolled sleeves, brown chinos and brown leather shoes'),
 ('shemagh', 'Şemağlı', 'a stocky middle-aged man with a grey-flecked beard, a red-and-white checkered shemagh with black agal, a black utility vest over a long beige shirt, olive cargo pants and tan work boots'),
]
NEW = [
 ('tourist', 'Turist', 'a sunburnt middle-aged European tourist in a wide straw hat, a loud orange Hawaiian shirt, beige cargo shorts, white socks with sandals and a big camera around his neck'),
 ('courier', 'Kurye', 'a young delivery rider in a blue-and-white jacket, an open-face motorcycle helmet, a square insulated delivery backpack, black trousers and sneakers'),
 ('suit', 'Takım elbiseli', 'a slick businessman in a tight navy suit with an open white collar, slicked-back hair, sunglasses pushed up on his head, a phone in one hand and pointed brown shoes'),
 ('teen', 'Genç', 'a skinny teenager in an oversized purple hoodie, big headphones around his neck, baggy grey jeans and chunky white sneakers'),
 ('fisher', 'Balıkçı', 'a stocky fisherman in a yellow waterproof apron over a blue-and-white striped shirt with rolled sleeves, black rubber boots and a navy woollen cap'),
 ('uncle', 'Amca', 'a big-bellied older man with a grey moustache, a white sleeveless vest, loose brown sirwal trousers, plastic slippers and prayer beads in his hand'),
]
POSES = [
 ('hit1', 'Yanağını tutuyor', 'portrait 2:3',
  "He has just been slapped hard on his RIGHT cheek by someone standing to his right. He stands with feet planted, head turned slightly to his left, eyes squeezed shut, mouth open in a pained \"ouch\", his RIGHT hand pressed flat against his right cheek, his left arm half raised in shock. Front view facing the camera, camera at chest height."),
 ('hit2', '45° yana eğilip korunuyor', 'portrait 2:3',
  "After a second slap from someone on his right, he leans his whole upper body about 45 degrees to HIS LEFT (towards the right side of the image), bending sideways at the waist, feet still planted shoulder-width apart, both forearms raised in front of his face defensively, flinching, one eye peeking out, frightened and pleading. Front view facing the camera, camera at chest height."),
 ('fall', 'Tekmeyle devriliyor', 'portrait 2:3',
  "He has just been kicked on his RIGHT hip and is falling sideways to HIS LEFT (towards the right side of the image): body tilted about 60 degrees, right leg lifted off the ground, arms flailing outward, shocked face with mouth wide open. Only his left foot still touches the ground. Front view, camera at chest height."),
 ('down', 'Yerde yatıyor', 'landscape 3:2',
  "He lies flat on his back on the ground after a fall, dazed, arms spread out, eyes closed. His feet point towards the camera and his head away from it; the camera is at standing eye level about two metres in front of his feet, looking slightly down. The whole body fits in the frame with margin."),
]
cards = []  # (section, title, tool, attach_img or None, attach_note, output file, prompt)
SHEET_BG = ("Background: perfectly flat solid chroma-key green (#00B140) across the whole image, no gradient, no floor, no cast shadows, no props. "
            "He wears nothing green. Photorealistic, identical soft frontal studio lighting on all five, sharp focus, no motion blur. No text, no numbers, no labels, no logo, no watermark, no border.")
def sheet_prompt(ref_sentence, desc):
    return (f"{ref_sentence} Keep exactly this man: {desc}.\n\n"
        "Create ONE wide 16:9 image that shows this same man FIVE times, side by side in a single row, left to right, like a character pose sheet. "
        "All five figures are the same size and scale, full body from head to shoes, feet on the same baseline, evenly spaced with a wide empty gap of background between neighbours, "
        "no figure touching or overlapping another. The same clothes and accessories in all five. Front view, camera at chest height for all of them. "
        "In every pose someone stands to HIS RIGHT side (the left side of the image), but that person is NOT shown.\n\n"
        "1. Neutral: standing upright and relaxed facing the camera, arms at his sides, neutral expression.\n"
        "2. Slapped: just slapped hard on his RIGHT cheek; feet planted, head turned slightly to his left, eyes squeezed shut, mouth open in a pained \"ouch\", his RIGHT hand pressed flat on his right cheek, left arm half raised in shock.\n"
        "3. Dodging: his whole upper body leaning about 45 degrees to HIS LEFT (towards the right of the image), bending sideways at the waist, feet planted, both forearms raised in front of his face, flinching, one eye peeking out, frightened.\n"
        "4. Kicked: falling sideways to HIS LEFT after a kick on his right hip, body tilted about 60 degrees, right leg lifted off the ground, arms flailing, shocked open mouth, only his left foot still touching the ground.\n"
        "5. Knocked down: lying flat on his back on the ground, dazed, eyes closed, arms spread, feet pointing towards the camera and head away from it, seen from slightly above.\n\n" + SHEET_BG)
REF_EXISTING = ("Use the attached reference image: it shows the same man twice, a small walking frame on the left (his outfit) and a large sharp photo on the right (his face, hair, beard and build).")
DONE = {'tank', 'thobe'}
for mid, tr, desc in MEN:
    if mid in DONE: continue
    cards.append((f'{tr} ({mid})', '5 poz tek görselde', 'Gemini · görsel 16:9', f'man_{mid}.png', 'En-boy oranını 16:9 seç.', f'man_{mid}_sheet.png', sheet_prompt(REF_EXISTING, desc)))
cards.append(('Beyaz thobe (thobe)', 'Sadece kaçma pozu (düzeltme)', 'Gemini · görsel', None,
  'Daha önce ürettiğin man_thobe_ref.jpg (ayakta duran, net) görselini ekle. Diğer 4 pozu tamam.', 'man_thobe_hit2.png',
  "Use the attached reference photo: keep exactly the same man, face, beard, white thobe, white ghutra with black agal and brown sandals. "
  "Show him ONCE, with exactly one head: after a second slap from someone on his right, he leans his whole upper body about 45 degrees to HIS LEFT (towards the right side of the image), "
  "bending sideways at the waist, feet still planted shoulder-width apart, both forearms raised in front of his face defensively, flinching, one eye peeking out, frightened. "
  "Front view, camera at chest height. " + tech()))
GR = ("the same elderly woman as in the attached reference (black headscarf, brown patterned cardigan with dark trim, red skirt with pink flowers, grey trousers, beige socks, burgundy shoes)")
sec = 'Granma tekme'
cards.append((sec, 'Tekme: 3 kare tek görselde', 'Gemini · görsel 16:9', 'granma_back_view.png', 'En-boy oranını 16:9 seç.', 'granma_kick_sheet.png',
  f"Use the attached reference image: it shows {GR}, from behind, at low resolution. Keep exactly this woman and her clothes.\n\n"
  "Create ONE wide 16:9 image that shows her THREE times, side by side in a single row, left to right, as the three phases of one kick. All three are seen from DIRECTLY BEHIND at chest height (we see her back, not her face), "
  "same size and scale, full body from headscarf to shoes, feet on the same baseline, with a wide empty gap between the figures, no figure touching or overlapping another. "
  "Her target stands to HER RIGHT (the right side of the image), but that person is NOT shown.\n\n"
  "1. Wind-up: weight on her left leg, right knee lifted and chambered towards her body, arms out for balance, leaning slightly to her left.\n"
  "2. Kick: her RIGHT leg fully extended sideways to her right at hip height, sole of the shoe pointing right, torso leaning to her left, skirt flaring, arms out.\n"
  "3. Recover: right foot coming back down next to the left, body straightening, arms lowering.\n\n"
  "Background: perfectly flat solid chroma-key green (#00B140) across the whole image, no gradient, no floor, no cast shadows, no props. Photorealistic, identical soft studio lighting, sharp focus, no motion blur. "
  "No text, no numbers, no labels, no logo, no watermark, no border."))
cards.append((sec, 'Tekme videosu (daha akıcı, isteğe bağlı)', 'Gemini · video', 'granma_back_view.png', 'Video üretebiliyorsan bunu da dene; olursa 3 kare yerine onu kullanırım.', 'granma_kick.mp4',
  f"A 3-second video of {GR}, seen from directly behind at chest height, on a perfectly flat chroma-key green background (#00B140). She stands still, shifts her weight onto her left leg, then delivers one strong sideways kick with her RIGHT leg out to her right side at hip height, skirt swinging, arms out for balance, holds the kick for a moment, then puts the foot back down and stands normally again. Static camera, full body always in frame with margin, no cast shadow, no other people, no text, no logo, no watermark."))
for mid, tr, desc in NEW:
    sec = f'Yeni: {tr} ({mid})'
    cards.append((sec, 'Temel görsel', 'Gemini · görsel', None, 'Referans yok. Sonraki kartlarda bu görseli ekleyeceksin.', f'man_{mid}_base.png',
      f"Full-body photo of {desc}, standing upright facing the camera, arms relaxed at his sides, neutral slightly cocky expression, camera at chest height. {tech()}"))
    cards.append((sec, 'Yürüme videosu', 'Viggle', None, f'man_{mid}_base.png görselini Viggle\'a yükle, "walk towards camera" şablonu, yeşil fon. Mümkünse ücretli plan (filigransız).', f'man_{mid}_walk.mp4', None))
    cards.append((sec, '5 poz tek görselde', 'Gemini · görsel 16:9', None, f'man_{mid}_base.png görselini ekle, en-boy oranını 16:9 seç.', f'man_{mid}_sheet.png',
      sheet_prompt("Use the attached reference photo.", desc)))
imgs = {n: thumb(n) for n in sorted({c[3] for c in cards if c[3]})}
data = [dict(sec=c[0], title=c[1], tool=c[2], img=c[3], note=c[4], file=c[5], prompt=c[6]) for c in cards]
tpl = open(os.path.join(os.path.dirname(__file__), 'prompt_page.tpl.html')).read()
out = tpl.replace('/*DATA*/', 'const CARDS=' + json.dumps(data, ensure_ascii=False) + ';const IMGS=' + json.dumps(imgs) + ';')
open(OUT, 'w').write(out); print(len(cards), 'cards', round(len(out)/1e6, 2), 'MB')
