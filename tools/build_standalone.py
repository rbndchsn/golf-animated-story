#!/usr/bin/env python3
"""Generate a truly self-contained HTML file that works by double-clicking.
No network, build tools, font downloads, or runtime dependencies required.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent.parent
text=(ROOT/'index.html').read_text('utf8')
for style in ['css/site.css','css/animations.css']:
  css=(ROOT/style).read_text('utf8')
  text=text.replace(f'<link rel="stylesheet" href="{style}">','<style>\n'+css+'\n</style>')
for js in ['data/scenes.js','data/illustrations.js','js/motion.js','js/app.js']:
  text=text.replace(f'<script src="{js}" defer></script>','')
js='\n'.join((ROOT/p).read_text('utf8') for p in ['data/scenes.js','data/illustrations.js','js/motion.js','js/app.js'])
text=text.replace('</body>',f'<script>\n{js}\n</script>\n</body>')
# Embedded cover icon and the social preview path are intentionally not part of the offline bundle.
# Browsers simply omit the favicon on a standalone file; the story itself is entirely self-contained.
out=ROOT/'dist'/'Golf_The_Game_Beneath_The_Game_Standalone.html';out.parent.mkdir(exist_ok=True)
out.write_text(text,'utf8');print(f'Built {out} ({out.stat().st_size//1024} KiB)')
