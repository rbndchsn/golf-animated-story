#!/usr/bin/env python3
"""Split the MP4 into small GitHub-safe binary objects and generate a byte-verified manifest.

The browser reconstructs the *exact* MP4 as one Blob before playing.
Run after `python tools/produce_film.py assemble`.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
film=ROOT/'film'
source=film/'export/The_Game_Beneath_The_Game_Full_Film.mp4'
raw=source.read_bytes();chunk_size=1_700_000
output=film/'chunks';output.mkdir(parents=True,exist_ok=True)
parts=[]
for i,offset in enumerate(range(0,len(raw),chunk_size)):
    name=f'film_{i:02d}.part';data=raw[offset:offset+chunk_size]
    (output/name).write_bytes(data)
    parts.append({'path':f'film/chunks/{name}','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
assert raw==b''.join((output/Path(p['path']).name).read_bytes() for p in parts)
manifest={'filename':source.name,'title':'The Game Beneath the Game?','mimeType':'video/mp4','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'durationSeconds':762.733,'chunks':parts}
(film/'film_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
print(f'Generated {len(parts)} pieces for {source.name} ({len(raw)} bytes).')
