#!/usr/bin/env python3
"""Reproducible offline narrated motion-comic film.

The movie uses the public hand-curated 43-scene script and SVG art.
Offline voice synthesis via FFmpeg/flite is deliberately disclosed.
Requires ffmpeg, cairoSVG, Pillow, NumPy, SoundFile.
No network, no secrets, no third-party copyrighted music.

Usage:
  python tools/produce_film.py prepare
  python tools/produce_film.py render
  python tools/produce_film.py assemble
"""
import json, re, os, sys, textwrap, subprocess, math, time, unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import soundfile as sf
import cairosvg

ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'film'
AUDIO=WORK/'audio'
STILLS=WORK/'stills'
CLIPS=WORK/'clips'
EXPORT=WORK/'export'
for x in (AUDIO,STILLS,CLIPS,EXPORT):x.mkdir(parents=True,exist_ok=True)
SCENES=json.loads((ROOT/'data'/'scenes.js').read_text('utf8').split('window.GOLF_SCENES = ',1)[1].rsplit(';',1)[0])
assert len(SCENES)==43
SIZE=(1280,720)
INK=(11,32,33); DEEP=(16,43,44); GOLD=(230,186,108); CREAM=(248,241,225); GOLD2=(255,213,146); PALE=(204,221,210); PAPER=(255,251,243); PARCHMENT=(230,222,207); TEAL=(139,197,188); PINK=(205,139,122)
FONTREG='/usr/share/fonts/truetype/clear-sans/ClearSans-Regular.ttf'
FONTBOLD='/usr/share/fonts/truetype/clear-sans/ClearSans-Bold.ttf'
FONTSER='/usr/share/fonts/truetype/charis/CharisSIL-Regular.ttf'
FONTS={}
def f(name,size):
  k=(name,size)
  if k not in FONTS: FONTS[k]=ImageFont.truetype({'reg':FONTREG,'bold':FONTBOLD,'ser':FONTSER}[name],size)
  return FONTS[k]

def run(args,timeout=180,quiet=True):
  p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
  if p.returncode!=0:raise RuntimeError(f'Command failed {args[:6]}\n{p.stderr[-1500:]}')
  return p.stdout

def sanitized(s):
  s=s.replace('→',' to ').replace('≠',' is not ').replace('·',', ').replace('−','minus ')
  s=s.replace('—',', ').replace('–',' to ').replace('“','').replace('”','').replace('’',"'").replace('…','...')
  s=s.replace(' / ',' or ')
  s=re.sub(r'\s+',' ',s).strip()
  # flite can read mixed unicode but normalize ligatures and accented characters.
  return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode('ascii')

def speech_name(n,who):return f'{n:02d}_{who}'

def synth_one(name,txt,voice):
  txt_path=AUDIO/(name+'.txt'); out=AUDIO/(name+'.wav')
  txt_path.write_text(sanitized(txt),encoding='utf8')
  if out.exists() and out.stat().st_size>2000:return (name,float(sf.info(out).duration))
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','lavfi','-i',f'flite=textfile={txt_path}:voice={voice}','-af','highpass=f=75,lowpass=f=8500,acompressor=threshold=-23dB:ratio=1.6:attack=18:release=120','-ar','24000','-ac','1',str(out)])
  return (name,float(sf.info(out).duration))

STATUS={'FACT':('HISTORICAL RECORD',TEAL),'LENS':('SYMBOLIC READING',GOLD),'MIX':('RECORD + READING',PARCHMENT),'OPEN':('OPEN QUESTION',PINK)}
ACTS=[(1,'I','THE ORIGINS','A game becomes a language.',(212,183,119)),(6,'II','THE READING','The symbols begin to accumulate.',GOLD),(20,'III','THE RIVALS','A game of status, competition and myth.',TEAL),(28,'IV','THE CHILDREN','The record changes the conversation.',PINK),(39,'V','THE INQUIRY','A darker question enters the archive.',PINK)]

# Render accessible, cinematic typography and faithful original SVG illustration.
def textbox(draw,text,xy,width,font,fill,spacing=5,maxlines=None):
  x,y=xy
  words=text.split();lines=[];line=''
  for word in words:
    trial=(line+' '+word).strip()
    if draw.textbbox((0,0),trial,font=font)[2]<=width:line=trial
    else:
      if line:lines.append(line)
      line=word
  if line:lines.append(line)
  if maxlines and len(lines)>maxlines:
    lines=lines[:maxlines]
    while lines[-1] and draw.textbbox((0,0),lines[-1]+'...',font=font)[2]>width:lines[-1]=lines[-1][:-1]
    lines[-1]+='...'
  h=font.size+spacing
  for l in lines:draw.text((x,y),l,font=font,fill=fill,stroke_width=0);y+=h
  return y

def roundbox(d,box,fill,r=18,outline=None,width=1):d.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=width)

def gradient_bg():
  im=Image.new('RGB',SIZE); pix=im.load()
  # In-camera green-black gradient with a warm spotlight in top right.
  yv=np.linspace(0,1,SIZE[1])[:,None];xv=np.linspace(0,1,SIZE[0])[None,:]
  planes=[]
  for c,(a,b) in enumerate([(11,18),(32,56),(33,54)]):
    a0=np.clip(a+(b-a)*(0.46*xv+0.48*yv),0,255)
    light=(np.exp(-((xv-.89)**2/.07+(yv-.08)**2/.15))*4).astype('float32')
    arr=np.clip(a0+light,0,255).astype('uint8')
    plane=Image.fromarray(np.broadcast_to(arr,SIZE[::-1]).copy(),'L')
    planes.append(plane)
  return Image.merge('RGB',planes)
BG=gradient_bg()

def avatar(d,who,x,y,active):
  accent=GOLD if who=='Q' else TEAL
  outline=(33,53,55)
  cx=x+26;cy=y+25
  d.ellipse((cx-22,cy-22,cx+22,cy+22),fill=(255,252,243),outline=outline,width=3)
  if who=='V':
    d.rectangle((cx-16,cy-3,cx-2,cy+8),outline=(45,113,106),width=2)
    d.rectangle((cx+2,cy-3,cx+16,cy+8),outline=(45,113,106),width=2)
    d.line((cx-2,cy+1,cx+2,cy+1),fill=(45,113,106),width=2)
  d.ellipse((cx-7,cy-2,cx-4,cy+1),fill=outline);d.ellipse((cx+5,cy-2,cx+8,cy+1),fill=outline)
  d.arc((cx-8,cy+3,cx+8,cy+15),0,180,fill=outline,width=2)
  d.line((cx,cy+22,cx,cy+47),fill=accent,width=6)
  d.line((cx,cy+30,cx-18,cy+41),fill=outline,width=3)
  d.line((cx,cy+30,cx+20,cy+37 if active else cy+44),fill=outline,width=3)
  d.line((cx,cy+47,cx-14,cy+64),fill=outline,width=3)
  d.line((cx,cy+47,cx+14,cy+64),fill=outline,width=3)

def make_scene_image(s,beat,art):
  im=BG.copy();d=ImageDraw.Draw(im)
  n=s['number'];st=s['status'];status,color=STATUS[st]
  d.text((48,22),'THE NINETEENTH HOLE  /  A MOTION COMIC',font=f('bold',16),fill=GOLD)
  d.text((48,56),s['title'],font=f('ser',42 if len(s['title'])<29 else 34),fill=CREAM)
  d.text((1230,31),f'FIELD NOTE  {n:03d} / 043',font=f('bold',16),fill=PALE,anchor='ra')
  d.line((48,113,1232,113),fill=(68,105,99),width=2)
  # Illustration card, exactly original vector artwork, with no cropping.
  roundbox(d,(45,135,839,565),PAPER,20,outline=(236,223,195),width=4)
  iw,ih=art.size; scale=min(778/iw,410/ih); art2=art.resize((int(iw*scale),int(ih*scale)),Image.Resampling.LANCZOS)
  im.paste(art2,(53+(778-art2.width)//2,144+(410-art2.height)//2))
  # Evidence box
  roundbox(d,(855,135,1233,565),(25,59,61),20,outline=(69,105,97),width=2)
  d.text((880,161),f'FIELD NOTE  {n:03d}',font=f('bold',16),fill=(181,212,201))
  roundbox(d,(879,194,1208,228),tuple(min(255,int(c*.30+25)) for c in color),17,outline=color,width=1)
  d.text((1043,201),status,font=f('bold',15),fill=color,anchor='ma')
  if beat==0:
    d.text((880,255),'01  /  THE QUESTION',font=f('bold',15),fill=GOLD)
    textbox(d,s['quinn'],(879,303),323,f('ser',28),CREAM,7,6)
    d.text((879,511),'A QUESTION TAKES SHAPE',font=f('bold',14),fill=(161,195,185))
  elif beat==1:
    d.text((880,253),'02  /  THE RESPONSE',font=f('bold',15),fill=TEAL)
    textbox(d,s['vale'],(879,302),329,f('ser',27),CREAM,6,7)
    d.text((879,514),'THE RECORD ENTERS',font=f('bold',14),fill=(161,195,185))
  else:
    d.text((880,254),'03  /  THE REVEAL',font=f('bold',16),fill=color)
    textbox(d,s['clue'],(879,308),322,f('ser',27),CREAM,8,6)
    if s.get('sourceName') and s['sourceName']!='Private hypothesis dossier: Golf_hypothesis_v1.md (not included in the site)':
      d.line((879,493,1206,493),fill=(75,115,108),width=1)
      textbox(d,s['sourceName'],(880,503),322,f('reg',15),PALE,2,2)
  # Dialogue, preserve text throughout 3 stages so film works without audio.
  for who,x1,x2,line in [('Q',46,628,s['quinn']),('V',641,1233,s['vale'])]:
    highlight=(who=='Q' and beat==0) or (who=='V' and beat==1)
    cardfill=(249,244,230) if who=='Q' else (230,239,233)
    if not highlight and beat in (0,1):cardfill=(221,220,202) if who=='Q' else (205,218,208)
    roundbox(d,(x1,579,x2,692),cardfill,17,outline=(251,209,139) if highlight else (152,172,157),width=3 if highlight else 1)
    avatar(d,who,x1+17,591,highlight)
    d.text((x1+93,592),'QUINN / THE QUESTIONER' if who=='Q' else 'VALE / THE ARCHIVIST',font=f('bold',15),fill=(160,101,46) if who=='Q' else (52,120,112))
    textbox(d,line,(x1+93,617),x2-x1-110,f('bold',18 if len(line)>100 else 20),INK,5,3)
  # progress on dark background bottom
  fillpct=n/len(SCENES);d.rounded_rectangle((46,702,1233,708),radius=3,fill=(73,105,99));d.rounded_rectangle((46,702,46+int(1187*fillpct),708),radius=3,fill=GOLD)
  return im

def make_title(title,kicker,subtitle,accent=GOLD,tag='A FIVE-ACT INQUIRY'):
  im=BG.copy();d=ImageDraw.Draw(im)
  d.ellipse((860,-130,1400,420),outline=(60,100,91),width=3);d.ellipse((905,-70,1340,355),outline=(82,117,99),width=2)
  d.rounded_rectangle((65,67,1207,656),radius=24,outline=(68,102,96),width=3)
  d.text((120,135),'THE NINETEENTH HOLE',font=f('bold',20),fill=accent)
  d.text((120,204),kicker.upper(),font=f('bold',19),fill=PALE)
  textbox(d,title,(120,280),1000,f('ser',88 if len(title)<18 else 68),CREAM,10,3)
  d.text((120,510),subtitle,font=f('reg',24),fill=PALE)
  d.line((120,570,1165,570),fill=accent,width=4)
  d.text((120,599),tag,font=f('bold',18),fill=accent)
  return im

def make_ending():
  im=BG.copy();d=ImageDraw.Draw(im)
  d.text((100,85),'THE GAME BENEATH THE GAME?',font=f('ser',62),fill=CREAM)
  d.text((100,195),'THE INQUIRY CONTINUES',font=f('bold',24),fill=GOLD)
  textbox(d,'A coherent symbolic interpretation is not the same as a proven historical origin.',(100,267),1040,f('ser',39),CREAM,7,3)
  textbox(d,'The history of child caddies is documented. Organized trafficking through golf institutions remains an unverified hypothesis.',(100,400),1050,f('reg',24),PALE,7,3)
  d.line((100,550,1185,550),fill=TEAL,width=3)
  d.text((100,583),'EXPLORE THE 43-SCENE INTERACTIVE EXHIBIT',font=f('bold',19),fill=GOLD)
  d.text((100,621),'rbndchsn.github.io/golf-animated-story/',font=f('reg',23),fill=PALE)
  return im

# audio timeline: arrange voice with pacing per beat + chapter transitions.
# segment IDs, images, spoken text, voice, duration and cumulative time.
def make_plan():
  print('Generating voice clips...',flush=True)
  voice_tasks=[]
  voice_tasks.append(('intro','The Game Beneath the Game. An illustrated inquiry in five acts. Two people, one hypothesis, and a trail of historical questions.','rms'))
  for i,s in enumerate(SCENES):
    if s['number'] in [1,6,20,28,39]:
      act=next(a for a in ACTS if a[0]==s['number'])
      voice_tasks.append((f'act_{act[1]}',act[2]+'. '+act[3],'rms'))
    voice_tasks.extend([(speech_name(s['number'],'q'),s['quinn'],'slt'),(speech_name(s['number'],'v'),s['vale'],'awb'),(speech_name(s['number'],'c'),s['clue'],'rms')])
  voice_tasks.append(('outro','The game is real. The interpretation is coherent as metaphor. The historical verdict is open. Continue the investigation and examine the sources.','rms'))
  dims={}
  with ThreadPoolExecutor(max_workers=4) as pool:
    for future in as_completed([pool.submit(synth_one,*x) for x in voice_tasks]):
      name,length=future.result();dims[name]=length
  print('Voice clips generated:',len(dims),flush=True)
  plan=[]; t=0.0
  def add(kind,name,scene,beat,voice_key,duration,image):
    nonlocal t
    entry=dict(kind=kind,name=name,scene=scene,beat=beat,voice=voice_key,start=round(t,3),duration=round(duration,3),image=str(image.relative_to(ROOT)))
    plan.append(entry);t+=duration
  add('intro','intro',0,None,'intro',dims['intro']+2.5,STILLS/'intro.png')
  for s in SCENES:
    act=next((a for a in ACTS if a[0]==s['number']),None)
    if act:
      k=f'act_{act[1]}'
      add('act',k,s['number'],None,k,dims[k]+1.8,STILLS/(k+'.png'))
    for beat,who in enumerate(['q','v','c']):
      name=speech_name(s['number'],who)
      gap=(1.2 if beat==2 else .5) + (.35 if s['number'] in (28,30,39,43) else 0)
      add('scene',name,s['number'],beat,name,dims[name]+gap,STILLS/(name+'.png'))
  add('outro','outro',44,None,'outro',dims['outro']+4,STILLS/'outro.png')
  (WORK/'timeline.json').write_text(json.dumps({'duration':round(t,3),'fps':15,'size':SIZE,'segments':plan},indent=2),encoding='utf8')
  print('Timeline',len(plan),'segments',round(t,1),'seconds',flush=True)
  return plan,t

def make_stills(plan):
  import io
  arts={}
  for s in SCENES:
    art=ROOT/s['svgFile']
    png=cairosvg.svg2png(url=str(art),output_width=1000,output_height=540)
    arts[s['number']]=Image.open(io.BytesIO(png)).convert('RGB')
  for i,p in enumerate(plan):
    dest=ROOT/p['image']
    if dest.exists() and dest.stat().st_size>1000:continue
    if p['kind']=='scene':im=make_scene_image(SCENES[p['scene']-1],p['beat'],arts[p['scene']])
    elif p['kind']=='intro':im=make_title('THE GAME BENEATH THE GAME?','WELCOME TO THE CLUBHOUSE','A question, a response, and a clue. Forty-three times.',tag='43 SCENES  ·  TWO VOICES  ·  THE RECORD')
    elif p['kind']=='act':
      a=next(a for a in ACTS if p['name']==f'act_{a[1]}')
      im=make_title(a[2],f'ACT {a[1]}',a[3],a[4],tag='HISTORICAL RECORD  /  SYMBOLIC INTERPRETATION  /  OPEN QUESTION')
    else:im=make_ending()
    dest.parent.mkdir(exist_ok=True,parents=True)
    im.save(dest,optimize=True)
  print('Stills generated.',len(plan),flush=True)

def create_soundtrack(plan,total):
  # Narration is aligned with visual beats, using a single 24kHz mono timeline.
  sr=24000
  samples=int((total+.2)*sr)
  mix=np.zeros(samples,dtype='float32')
  for p in plan:
    y,s=sf.read(AUDIO/(p['voice']+'.wav'),dtype='float32')
    if y.ndim==2:y=y.mean(axis=1)
    start=int((p['start']+.2)*sr)
    end=min(start+len(y),len(mix))
    if end>start:
      # Normalize speech peak, mix voice over low-level original ambient bed.
      pk=max(.05,np.max(np.abs(y)))
      mix[start:end]+=(y[:end-start] * (.77/pk))
  # Original unobtrusive ambient: breathy pentatonic drone, different harmonic hue by act.
  # No licensed music, no generated music based on a copyrighted song.
  phase=np.arange(samples,dtype='float64')/sr
  amb=np.zeros(samples,dtype='float32')
  chord_roots=[110.0,130.81,146.83,98.0,82.41]
  for j,p in enumerate(plan):
    a=int(p['start']*sr);b=min(samples,int((p['start']+p['duration'])*sr))
    if b<=a:continue
    act_index=0
    if p['scene']>0:
      for m,act in enumerate(ACTS):
        if p['scene']>=act[0]:act_index=m
    root=chord_roots[act_index]
    sl=phase[a:b]; slowly=(np.sin(2*np.pi*.038*sl)**2)*.32+.68
    waveform=(np.sin(2*np.pi*root*.5*sl)+.42*np.sin(2*np.pi*root*.749*sl)+.36*np.sin(2*np.pi*root*1.249*sl))*0.009
    amb[a:b]+=(waveform*slowly).astype('float32')
  # very subtle ambient sound, mastered to avoid clipping
  mix=np.clip(mix+amb,-.95,.95)
  sf.write(str(EXPORT/'soundtrack.wav'),mix,sr,subtype='PCM_16')
  # Build VTT captions with speaker cues so viewers can turn on captions in browser.
  def stamp(t):
    m,s=divmod(t,60);h,m=divmod(int(m),60)
    return f'{h:02}:{m:02}:{s:06.3f}'
  lines=['WEBVTT','']
  for p in plan:
    if p['kind']=='scene':
      s=SCENES[p['scene']-1]
      sp={'q':'Quinn','v':'Vale','c':'Field note'}[p['name'][-1]]
      txt={'q':s['quinn'],'v':s['vale'],'c':s['clue']}[p['name'][-1]]
    elif p['kind']=='act':
      a=next(a for a in ACTS if p['name']==f'act_{a[1]}');sp=f'Act {a[1]}';txt=a[2]+'. '+a[3]
    elif p['kind']=='intro':sp='Narrator';txt='The Game Beneath the Game? An illustrated inquiry in five acts.'
    else:sp='Narrator';txt='The game is real. The interpretation is coherent as metaphor. The historical verdict is open.'
    lines.extend([f"{stamp(p['start']+.15)} --> {stamp(p['start']+p['duration']-.15)}",f'{sp}: {txt}',''])
  (EXPORT/'captions.vtt').write_text('\n'.join(lines),encoding='utf8')
  # Chapters needed for linked web player navigation
  chapters=[dict(title=a[2].title(),start=next(p['start'] for p in plan if p['name']==f'act_{a[1]}'),scene=a[0]) for a in ACTS]
  (EXPORT/'chapters.json').write_text(json.dumps(chapters,indent=2),encoding='utf8')
  print('Soundtrack, captions and chapters ready.',flush=True)

def render_one(p):
  name=p['name'];still=ROOT/p['image'];clip=CLIPS/(name+'.mp4')
  if clip.exists() and clip.stat().st_size>5000:return (name,'cached',clip.stat().st_size)
  # Smooth slow camera push with slight vertical drift, vector art stays readable.
  # Each beat is its own H264-only segment (muxed with narration after concatenation).
  fps=15
  zoom="min(zoom+0.00027,1.033)"
  x="iw/2-(iw/zoom/2)"
  y="ih/2-(ih/zoom/2)"
  filt=f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1280x720:fps={fps},format=yuv420p"
  cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-loop','1','-framerate',str(fps),'-i',str(still),'-vf',filt,'-t',f'{p["duration"]:.3f}','-c:v','libx264','-preset','ultrafast','-crf','30','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(clip)]
  run(cmd,timeout=180)
  return (name,'built',clip.stat().st_size)

def render_all(plan):
  start=time.monotonic()
  with ThreadPoolExecutor(max_workers=3) as ex:
    futs=[ex.submit(render_one,p) for p in plan]
    for n,q in enumerate(as_completed(futs),1):
      x=q.result()
      if n%25==0 or n==len(futs):print(f'Clips rendered: {n}/{len(futs)} in {time.monotonic()-start:.0f}s',flush=True)
  flist=WORK/'concat.txt'
  flist.write_text(''.join(f"file '{(CLIPS/(p['name']+'.mp4')).resolve()}'\n" for p in plan),encoding='utf8')
  print('All clips prepared.',flush=True)

def assemble(plan):
  target=EXPORT/'The_Game_Beneath_The_Game_Full_Film.mp4'
  # Two-pass export avoids slow clip demuxing and audio transcoding in one step.
  video_only=EXPORT/'video_only.mp4'
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(WORK/'concat.txt'),'-an','-c:v','copy','-movflags','+faststart',str(video_only)],timeout=180)
  # Recompress ultrafast source clips to an efficient streamable 720p web master.
  run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(video_only),'-i',str(EXPORT/'soundtrack.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','28','-pix_fmt','yuv420p','-c:a','aac','-b:a','48k','-ar','24000','-ac','1','-movflags','+faststart','-shortest','-metadata','title=The Game Beneath the Game? | The Nineteenth Hole',str(target)],timeout=300)
  meta=json.loads(run(['ffprobe','-v','quiet','-show_format','-show_streams','-of','json',str(target)]))
  (EXPORT/'render_report.json').write_text(json.dumps({'size_bytes':target.stat().st_size,'duration_seconds':float(meta['format']['duration']),'video_codec':next(x for x in meta['streams'] if x['codec_type']=='video')['codec_name'],'audio_codec':next(x for x in meta['streams'] if x['codec_type']=='audio')['codec_name'],'scenes':43,'chapters':5,'title':'The Game Beneath the Game?','voices':'Flite CMU slt, awb and rms synthetic voices','evidence':'Historical claims and speculative readings are differentiated in scenes.js'},indent=2),encoding='utf8')
  print('MASTER:',target,'MB:',target.stat().st_size/1e6,'duration',meta['format']['duration'],flush=True)
  return target

if __name__=='__main__':
  cmd=sys.argv[1] if len(sys.argv)>1 else 'prepare'
  if cmd=='prepare':
    plan,t=make_plan();make_stills(plan);create_soundtrack(plan,t)
  elif cmd=='render':
    plan=json.loads((WORK/'timeline.json').read_text())['segments'];render_all(plan)
  elif cmd=='assemble':
    plan=json.loads((WORK/'timeline.json').read_text())['segments'];assemble(plan)
  else: raise ValueError(cmd)
