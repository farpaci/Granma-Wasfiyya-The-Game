import base64, glob, io, json, os
from PIL import Image
MAMA_RS = 0.75   # Granma's walk/slap/kick art is shrunk to this fraction at inline time (the game divides it back out when drawing)
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
assets = {}
def b64s(f):
    im = Image.open(f); im.load(); b = io.BytesIO()
    im.resize((max(1, round(im.width * MAMA_RS)), max(1, round(im.height * MAMA_RS))), Image.LANCZOS).save(b, 'WEBP', quality=88, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()
def b64(f, mime): return f'data:{mime};base64,' + base64.b64encode(open(f, 'rb').read()).decode()
for f in sorted(glob.glob(os.path.join(root, 'assets', '*'))):
    name, ext = os.path.splitext(os.path.basename(f))
    if name.startswith('mama'): continue
    assets[name] = b64(f, 'image/jpeg' if ext == '.jpg' else 'image/png')
for f in sorted(glob.glob(os.path.join(root, 'assets_video', 'walk_*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64s(f)
for f in sorted(glob.glob(os.path.join(root, 'assets_slap', 'slap*.webp')) + glob.glob(os.path.join(root, 'assets_slap', 'kick_*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64s(f)
for f in sorted(glob.glob(os.path.join(root, 'assets_slap', 'sfx_*.mp3'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64(f, 'audio/mpeg')
for f in sorted(glob.glob(os.path.join(root, 'assets_enemy', '*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64(f, 'image/webp')
for f in sorted(glob.glob(os.path.join(root, 'assets_group', '*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64(f, 'image/webp')
mgroup = json.load(open(os.path.join(root, 'assets_group', 'meta_group.json')))
menemy = json.load(open(os.path.join(root, 'assets_enemy', 'meta_enemy.json')))
meta = json.load(open(os.path.join(root, 'assets_video', 'meta.json')))
mslap = json.load(open(os.path.join(root, 'assets_slap', 'meta_slap.json')))
src = open(os.path.join(root, 'src', 'game.slap.src.html'), encoding='utf-8').read()
out = src.replace('/*ASSETS*/', 'const MAMA_RS = ' + str(MAMA_RS) + ';\nconst ASSETS = ' + json.dumps(assets) + ';\nconst META = ' + json.dumps(meta) + ';\nconst META_SLAP = ' + json.dumps(mslap) + ';\nconst META_GROUP = ' + json.dumps(mgroup) + ';\nconst META_ENEMY = ' + json.dumps(menemy) + ';')
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', round(len(out)/1e6, 2), 'MB,', len(assets), 'assets')
