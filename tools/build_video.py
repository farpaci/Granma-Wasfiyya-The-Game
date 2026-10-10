import base64, glob, json, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
assets = {}
for f in sorted(glob.glob(os.path.join(root, 'assets', '*'))):
    name, ext = os.path.splitext(os.path.basename(f))
    if name.startswith('mama'): continue
    assets[name] = ('data:image/jpeg;base64,' if ext == '.jpg' else 'data:image/png;base64,') + base64.b64encode(open(f, 'rb').read()).decode()
for f in sorted(glob.glob(os.path.join(root, 'assets_video', 'walk_*.webp'))):
    name = os.path.splitext(os.path.basename(f))[0]
    assets[name] = 'data:image/webp;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
meta = json.load(open(os.path.join(root, 'assets_video', 'meta.json')))
src = open(os.path.join(root, 'src', 'game.video.src.html'), encoding='utf-8').read()
out = src.replace('/*ASSETS*/', 'const ASSETS = ' + json.dumps(assets) + ';\nconst META = ' + json.dumps(meta) + ';')
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', round(len(out)/1e6, 2), 'MB,', len(assets), 'assets')
