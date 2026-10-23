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
cards = []  # (section, title, tool, attach_img or None, attach_note, prompt)
for mid, tr, desc in MEN:
    sec = f'{tr} ({mid})'
    cards.append((sec, 'Net referans (önce bunu yap)', 'Gemini · görsel', f'man_{mid}.png', None, f'man_{mid}_ref.png',
      f"The attached image shows one man twice: a small low-resolution walking frame on the left (his outfit as seen in the game) and a large sharp photo on the right (his face, hair, beard and build). "
      f"Create a sharp, high-resolution full-body reference photo of this same man: same face, hair, beard and body as the large photo, wearing exactly the outfit of the small walking frame: {desc}. "
      f"He stands upright and relaxed facing the camera, arms at his sides, neutral expression, camera at chest height. {tech()}"))
    for pid, ptr, orient, pose in POSES:
        p = (f"Use the attached reference photo: keep exactly the same man, face, hair, beard, body and outfit: {desc}. "
             f"{pose} {tech(orient)}")
        cards.append((sec, ptr, 'Gemini · görsel', None, f'1. adımda ürettiğin man_{mid}_ref.png görselini ekle.', f'man_{mid}_{pid}.png', p))
GR = ("the same elderly woman as in the attached reference (black headscarf, brown patterned cardigan, red skirt with pink flowers, grey trousers, beige socks, burgundy shoes), "
      "seen from directly behind at chest height")
sec = 'Granma tekme'
cards.append((sec, 'Net referans (önce bunu yap)', 'Gemini · görsel', 'granma_back_view.png', None, 'granma_ref.png',
  "The attached image shows the same elderly woman four times from behind (walking and slapping), at low resolution. Create one sharp, high-resolution full-body reference photo of her: "
  "same body shape, black headscarf, brown patterned cardigan with dark trim, red skirt with pink flowers, grey trousers, beige socks and burgundy shoes. "
  "She stands upright and still, seen from directly behind at chest height, arms relaxed at her sides. " + tech()))
cards.append((sec, 'Tekme videosu (önerilen)', 'Gemini · video', None, '1. adımda ürettiğin granma_ref.png görselini ilk kare olarak ekle.', 'granma_kick.mp4',
  f"A 3-second video of {GR}, on a perfectly flat chroma-key green background (#00B140). She stands still, shifts her weight onto her left leg, then delivers one strong sideways kick with her RIGHT leg out to her right side at hip height, skirt swinging, arms out for balance, holds the kick for a moment, then puts the foot back down and stands normally again. Static camera, full body always in frame with margin, no cast shadow, no other people, no text, no logo, no watermark."))
for kid, ktr, pose in [('kick1', 'Tekme hazırlık (video yoksa)', "Her weight is on her left leg, her right knee lifted and chambered towards her body, arms out for balance, leaning slightly to her left."),
                       ('kick2', 'Tekme anı (video yoksa)', "Her RIGHT leg is fully extended sideways to her right at hip height, sole of the shoe pointing right, torso leaning to her left, skirt flaring, arms out."),
                       ('kick3', 'Tekme dönüş (video yoksa)', "Her right foot is coming back down next to the left, body straightening, arms lowering.")]:
    cards.append((sec, ktr, 'Gemini · görsel', None, '1. adımda ürettiğin granma_ref.png görselini ekle.', f'granma_{kid}.png', f"Show {GR}. {pose} {tech()}"))
for mid, tr, desc in NEW:
    sec = f'Yeni: {tr} ({mid})'
    cards.append((sec, 'Temel görsel', 'Gemini · görsel', None, 'Referans yok. Sonraki kartlarda bu görseli ekleyeceksin.', f'man_{mid}_base.png',
      f"Full-body photo of {desc}, standing upright facing the camera, arms relaxed at his sides, neutral slightly cocky expression, camera at chest height. {tech()}"))
    cards.append((sec, 'Yürüme videosu', 'Viggle', None, f'man_{mid}_base.png görselini Viggle\'a yükle, "walk towards camera" şablonu, yeşil fon. Mümkünse ücretli plan (filigransız).', f'man_{mid}_walk.mp4', None))
    for pid, ptr, orient, pose in POSES:
        cards.append((sec, ptr, 'Gemini · görsel', None, f'Az önce ürettiğin man_{mid}_base.png görselini ekle.', f'man_{mid}_{pid}.png',
          f"Use the attached reference image: keep exactly the same man, face, hair and outfit: {desc}. {pose} {tech(orient)}"))
imgs = {n: thumb(n) for n in sorted({c[3] for c in cards if c[3]})}
data = [dict(sec=c[0], title=c[1], tool=c[2], img=c[3], note=c[4], file=c[5], prompt=c[6]) for c in cards]
tpl = open(os.path.join(os.path.dirname(__file__), 'prompt_page.tpl.html')).read()
out = tpl.replace('/*DATA*/', 'const CARDS=' + json.dumps(data, ensure_ascii=False) + ';const IMGS=' + json.dumps(imgs) + ';')
open(OUT, 'w').write(out); print(len(cards), 'cards', round(len(out)/1e6, 2), 'MB')
