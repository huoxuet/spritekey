"""Verify the published whitelist; intentionally excludes the inventory itself."""
from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
inventory = json.loads((root / 'SOURCE-SHA256.json').read_text(encoding='utf-8'))
for name, expected in inventory['files'].items():
    relative = Path(name)
    if relative.is_absolute() or '..' in relative.parts:
        raise SystemExit('Unsafe inventory path: ' + name)
    path = root / relative
    if path.is_symlink() or not path.is_file():
        raise SystemExit('Missing or symlinked file: ' + name)
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise SystemExit('SHA256 mismatch: ' + name)
print('Verified', len(inventory['files']), 'public source files')
