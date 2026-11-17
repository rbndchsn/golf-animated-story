#!/usr/bin/env python3
"""Rebuild the offline SVG cache after editing assets/illustrations/*.svg.
Run from anywhere: python tools/sync_illustrations.py
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent.parent
FOLDER=ROOT/'assets'/'illustrations'
art={}
for p in sorted(FOLDER.glob('*.svg')):
  i=int(p.name[:2]);art[str(i)]=p.read_text('utf-8')
assert sorted(map(int,art.keys()))==list(range(1,44)), 'Expected 43 illustrations, 01-43.'
(ROOT/'data'/'illustrations.js').write_text('/* Generated from editable SVG assets; do not hand-edit. */\nwindow.GOLF_ILLUSTRATIONS = '+json.dumps(art,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf8')
print('Synchronized',len(art),'vector illustrations.')
