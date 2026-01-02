#!/usr/bin/env python3
import base64, hashlib, json, re
from pathlib import Path

manifest_path = Path('/var/www/API Juridica/websigner_ext/manifest.json')
native_manifest_path = Path('/etc/opt/chrome/native-messaging-hosts/br.com.softplan.webpki.json')

if not manifest_path.exists():
    print('ERROR: manifest.json not found at', manifest_path)
    raise SystemExit(1)

m = json.loads(manifest_path.read_text(encoding='utf-8'))
key_b64 = m.get('key')
if not key_b64:
    print('ERROR: "key" field not present in manifest.json')
    raise SystemExit(1)

try:
    key_bytes = base64.b64decode(key_b64)
except Exception as e:
    print('ERROR: failed to base64-decode key:', e)
    raise SystemExit(1)

sha = hashlib.sha256(key_bytes).digest()
first16 = sha[:16]

# map each nibble (4 bits) to a-p
def extid_from_bytes(bts):
    chars = []
    for b in bts:
        hi = (b >> 4) & 0xF
        lo = b & 0xF
        chars.append(chr(ord('a') + hi))
        chars.append(chr(ord('a') + lo))
    return ''.join(chars)

ext_id = extid_from_bytes(first16)
print('Computed extension ID:', ext_id)

# read native manifest and extract allowed origins
if not native_manifest_path.exists():
    print('WARN: native manifest not found at', native_manifest_path)
    allowed = []
else:
    try:
        nm = json.loads(native_manifest_path.read_text(encoding='utf-8'))
        allowed = nm.get('allowed_origins') or nm.get('allowed_extensions') or []
    except Exception as e:
        print('WARN: failed to read native manifest:', e)
        allowed = []

# normalize allowed origins to ids
allowed_ids = []
for a in allowed:
    m = re.search(r'chrome-extension://([a-p0-9]{32})/?', a)
    if not m:
        m = re.search(r'([a-p0-9]{32})', a)
    if m:
        allowed_ids.append(m.group(1))

print('Allowed IDs in native manifest:', allowed_ids)

if ext_id in allowed_ids:
    print('MATCH: computed extension ID is present in allowed_origins')
else:
    print('NO MATCH: computed extension ID not present in allowed_origins')
    if allowed_ids:
        print('You may need to add this ID to the native manifest allowed_origins or use the extension key that matches.')

