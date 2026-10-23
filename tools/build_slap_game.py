import base64, glob, json, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
assets = {}
def b64(f, mime): return f'data:{mime};base64,' + base64.b64encode(open(f, 'rb').read()).decode()
for f in sorted(glob.glob(os.path.join(root, 'assets', '*'))):
    name, ext = os.path.splitext(os.path.basename(f))
    if name.startswith('mama'): continue
    assets[name] = b64(f, 'image/jpeg' if ext == '.jpg' else 'image/png')
for f in sorted(glob.glob(os.path.join(root, 'assets_video', 'walk_*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64(f, 'image/webp')
for f in sorted(glob.glob(os.path.join(root, 'assets_slap', 'slap*.webp')) + glob.glob(os.path.join(root, 'assets_slap', 'kick_*.webp'))):
    assets[os.path.splitext(os.path.basename(f))[0]] = b64(f, 'image/webp')
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
out = src.replace('/*ASSETS*/', 'const ASSETS = ' + json.dumps(assets) + ';\nconst META = ' + json.dumps(meta) + ';\nconst META_SLAP = ' + json.dumps(mslap) + ';\nconst META_GROUP = ' + json.dumps(mgroup) + ';\nconst META_ENEMY = ' + json.dumps(menemy) + ';')
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', round(len(out)/1e6, 2), 'MB,', len(assets), 'assets')
