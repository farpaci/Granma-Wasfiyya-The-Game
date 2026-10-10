"""Inline every sprite as a data URL so index.html runs standalone (also avoids canvas taint on file://)."""
import base64, glob, json, os

root = os.path.dirname(os.path.abspath(__file__))
assets = {}
for f in sorted(glob.glob(os.path.join(root, 'assets', '*'))):
    name, ext = os.path.splitext(os.path.basename(f))
    mime = 'image/jpeg' if ext == '.jpg' else 'image/png'
    assets[name] = f'data:{mime};base64,' + base64.b64encode(open(f, 'rb').read()).decode()

src = open(os.path.join(root, 'game.src.html'), encoding='utf-8').read()
out = src.replace('/*ASSETS*/', 'const ASSETS = ' + json.dumps(assets) + ';')
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html', round(len(out) / 1e6, 2), 'MB,', len(assets), 'assets')
