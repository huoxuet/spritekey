"""Check the installed wheel, not src imports; exercise both original CLI demos."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import spritekey
from PIL import Image

root = Path(__file__).resolve().parents[1]
installed = Path(spritekey.__file__).resolve().parent
if installed == (root / 'src/spritekey').resolve():
    raise SystemExit('Expected wheel installation, got source import')
inventory = json.loads((root / 'SOURCE-SHA256.json').read_text(encoding='utf-8'))
prefix = 'src/spritekey/'
for name, expected in inventory['files'].items():
    if name.startswith(prefix):
        path = installed / name[len(prefix):]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, name
assert spritekey.__version__ == '0.4.0'
console = shutil.which('spritekey')
if console is None:
    raise SystemExit('Installed spritekey console script missing from PATH')
with tempfile.TemporaryDirectory(prefix='spritekey-install-') as scratch:
    for screen in ('green', 'blue'):
        demo = Path(scratch) / screen
        subprocess.run([sys.executable, '-m', 'spritekey.demo', str(demo), '--screen', screen], check=True, cwd=scratch)
        subprocess.run([console, '--config', str(demo / 'config.json')], check=True, cwd=scratch)
        output = demo / 'output'
        manifest = json.loads((output / 'manifest.json').read_text(encoding='utf-8'))
        assert manifest['frame_count'] == 3
        frames = list((output / 'frames').glob('*.png'))
        assert len(frames) == 3 and (output / 'preview.html').is_file()
        assert not (output / 'INCOMPLETE').exists()
        for frame in frames:
            with Image.open(frame) as image:
                assert image.mode == 'RGBA' and image.size == (192, 128)
print('Installed payload and green/blue console demos passed:', installed)
