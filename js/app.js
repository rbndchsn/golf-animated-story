/* Story runtime. Works as a plain file:// document or from any GitHub Pages subpath.
   No framework, network request, analytics, or external dependency. */
(()=>{
  'use strict';
  const S=window.GOLF_SCENES||[], A=window.GOLF_ILLUSTRATIONS||{}, Motion=window.GOLF_MOTION;
  if(S.length!==43 || !Motion){document.body.insertAdjacentHTML('beforeend','<p style="padding:16px">Story files are missing. Ensure index.html, data/ and js/ are all in the same project folder.</p>');return;}
  const $=id=>document.getElementById(id);
  const mql=window.matchMedia('(prefers-reduced-motion: reduce)');
  const reduced=()=>mql.matches;
  const label={
    FACT:{name:'HISTORICAL RECORD',css:'fact',clue:'A documented clue'},
    LENS:{name:'SYMBOLIC READING',css:'lens',clue:'Through the symbolic lens'},
    MIX:{name:'RECORD + INTERPRETATION',css:'mix',clue:'Two layers of meaning'},
    OPEN:{name:'OPEN QUESTION',css:'open',clue:'A question for the archives'}
  };
  const sections=[
    {first:0,last:4,name:'I · ORIGINS',act:'I'},
    {first:5,last:18,name:'II · THE READING',act:'II'},
    {first:19,last:26,name:'III · THE RIVALS',act:'III'},
    {first:27,last:37,name:'IV · THE CHILDREN',act:'IV'},
    {first:38,last:42,name:'V · THE INQUIRY',act:'V'}
  ];
  let idx=0,beat=0,playing=false,timer=null,sound=false,audioCtx=null, speed=1;
  let lastFocus=null, activeOverlay=null, touchStart=null;
  const clean=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const sceneLink=()=>{const url=new URL(window.location.href);url.hash=`scene=${idx+1}`;return url.href;};
  const describeStatus=s=>label[s.status]||label.OPEN;
  function sectionFor(i){return sections.find(n=>i>=n.first&&i<=n.last)||sections[0];}

  function avatar(who){
    let q=who==='quinn',accent=q?'#ba8a49':'#4f978e',body=q?'#e4ba73':'#82bbb0';
    return `<svg viewBox="0 0 90 96" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
      <g class="head"><circle cx="43" cy="24" r="18" fill="#fffcf4" stroke="#25383b" stroke-width="2.5"/>
        ${q?'<path d="M30 13q1-15 12-6q6-6 12 7" fill="none" stroke="#25383b" stroke-width="2.5" stroke-linecap="round"/>':'<path d="M30 11q12-13 25 0" stroke="#25383b" stroke-width="2.5" fill="none"/>'}
        <circle class="iris" cx="37" cy="24" r="1.7" fill="#25383b"/><circle class="iris" cx="49" cy="24" r="1.7" fill="#25383b"/>
        ${q?'':'<rect x="30" y="19" width="13" height="9" rx="3" fill="none" stroke="#367c77" stroke-width="1.6"/><rect x="45" y="19" width="13" height="9" rx="3" fill="none" stroke="#367c77" stroke-width="1.6"/><path d="M43 22h3" stroke="#367c77" stroke-width="1.4"/>'}
        <path d="M38 31q6 5 11-1" stroke="#25383b" stroke-width="1.9" fill="none" stroke-linecap="round"/>
      </g>
      <path d="M43 42V71" stroke="${accent}" stroke-width="6" stroke-linecap="round"/>
      <path d="M43 47L22 61" stroke="#25383b" stroke-width="3" stroke-linecap="round"/>
      <path class="arm-r" d="M43 47L66 60" stroke="#25383b" stroke-width="3" stroke-linecap="round"/>
      <path d="M43 71L25 92M43 71L62 92" stroke="#25383b" stroke-width="3" stroke-linecap="round"/>
      <path d="M37 44h12" stroke="${body}" stroke-width="5" stroke-linecap="round"/>
    </svg>`;
  }
  $('quinnAvatar').innerHTML=avatar('quinn');$('valeAvatar').innerHTML=avatar('vale');
  $('coverArt').innerHTML=A['1']||'';

  function chirp(kind){
    if(!sound)return;
    try{
      audioCtx ||= new (window.AudioContext||window.webkitAudioContext)();
      if(audioCtx.state==='suspended')audioCtx.resume();
      const now=audioCtx.currentTime;
      const notes=kind==='reveal'?[[520,0,.11],[760,.095,.17]]:[[390,0,.09]];
      notes.forEach(([hz,delay,duration])=>{
        const os=audioCtx.createOscillator(),gain=audioCtx.createGain();
        os.type='sine';os.frequency.setValueAtTime(hz,now+delay);
        gain.gain.setValueAtTime(0.0001,now+delay);
        gain.gain.linearRampToValueAtTime(.026,now+delay+.014);
        gain.gain.exponentialRampToValueAtTime(.0001,now+delay+duration);
        os.connect(gain).connect(audioCtx.destination);os.start(now+delay);os.stop(now+delay+duration+.01);
      });
    }catch(e){/* Audio is optional and must never interrupt the story. */}
  }
  function animateSketch(){
    if(reduced())return;
    const svg=$('sceneArt').querySelector('svg');if(!svg)return;
    let k=0;
    for(const el of svg.querySelectorAll('path[stroke],line[stroke],polyline[stroke]')){
      if(k>=22)break;
      const stroke=el.getAttribute('stroke');if(!stroke||stroke==='none')continue;
      try{const len=el.getTotalLength();if(len<14||len>1800)continue;
        el.style.setProperty('--len',String(len));el.style.setProperty('--d',`${(.06+(k%7)*.1).toFixed(2)}s`);el.classList.add('sketch-line');k++;
      }catch(e){/* Some old SVG shapes do not implement getTotalLength. */}
    }
    let j=0;
    for(const el of svg.querySelectorAll('text')){
      el.style.setProperty('--d',`${(.1+(j%8)*.12).toFixed(2)}s`);el.classList.add('stage-text');j++;
    }
  }
  function progress(){
    const percent=((idx+(beat+1)/3)/S.length*100);
    $('progressFill').style.width=percent.toFixed(2)+'%';
    $('progressBar').setAttribute('aria-valuenow',String(idx+1));
    const phases=['QUESTION','RESPONSE','CLUE'];
    $('progressCaption').textContent=`SCENE ${idx+1} OF ${S.length} · ${phases[beat]}`;
    for(const el of $('actTimeline').querySelectorAll('button')){
      const first=Number(el.dataset.target),sec=sections.find(n=>n.first===first);
      el.classList.toggle('active',idx>=sec.first&&idx<=sec.last);
      el.style.setProperty('--done', idx<sec.first?'0%':idx>sec.last?'100%':`${Math.min(100,Math.round((idx-sec.first+(beat+1)/3)/(sec.last-sec.first+1)*100))}%`);
    }
  }
  function setAdvance(){
    const text=beat===0?'HEAR THE RESPONSE  →':beat===1?'REVEAL THE CLUE  ✦':idx===S.length-1?'THE END · RESTART ↻':'NEXT SCENE  →';
    $('advanceButton').textContent=text;
  }
  function goto(index,{quiet=false}={}){
    clearTimeout(timer);timer=null;
    idx=(index+S.length)%S.length;beat=0;
    const s=S[idx],info=describeStatus(s),section=sectionFor(idx);
    $('story').dataset.act=section.act;
    $('actKicker').textContent=`ACT ${section.name} / ${s.act==='PROLOGUE'?'PROLOGUE':s.act==='EPILOGUE'?'EPILOGUE':'FIELD NOTES'}`;
    $('sceneTitle').textContent=s.title;
    $('sceneNumber').textContent=String(idx+1).padStart(2,'0');
    $('fieldNum').textContent=String(idx+1).padStart(3,'0');
    $('screenAct').textContent=s.act;
    $('screen').setAttribute('aria-label',`${s.title}: illustrated cartoon about ${s.visual.replaceAll('_',' ')}`);
    $('quinnLine').textContent=s.quinn;$('valeLine').textContent=s.vale;
    $('sceneArt').innerHTML=A[String(idx+1)]||'<p>Illustration unavailable.</p>';
    $('sceneArt').classList.remove('arriving');void $('sceneArt').offsetWidth;$('sceneArt').classList.add('arriving');
    $('quinnCard').classList.remove('hidden-beat');$('quinnCard').classList.add('appearing');
    $('quinnAvatar').classList.add('active');$('valeAvatar').classList.remove('active');
    $('valeCard').classList.add('hidden-beat');$('valeCard').classList.remove('appearing');$('valeCard').setAttribute('aria-hidden','true');
    $('desk').classList.remove('has-clue');$('clueContent').setAttribute('aria-hidden','true');
    $('kinetic').replaceChildren();$('clueTitle').textContent=info.clue;$('clueText').textContent=s.clue;
    $('statusTag').textContent=info.name;$('statusTag').className='status-pill '+info.css;
    $('backButton').disabled=(idx===0);
    $('announcer').textContent=`Scene ${idx+1}: ${s.title}. Quinn asks: ${s.quinn}`;
    try{window.history.replaceState(null,'',`#scene=${idx+1}`);}catch(e){window.location.hash=`scene=${idx+1}`;}
    const wipe=$('sceneCut');wipe.classList.remove('active');if(!reduced()){void wipe.offsetWidth;wipe.classList.add('active');}
    animateSketch();progress();setAdvance();if(!quiet)chirp('step');
    if(playing)schedule();
  }
  function advance(){
    clearTimeout(timer);timer=null;
    const s=S[idx];
    if(beat===0){
      beat=1;
      $('valeCard').classList.remove('hidden-beat');$('valeCard').classList.add('appearing');$('valeCard').setAttribute('aria-hidden','false');
      $('quinnAvatar').classList.remove('active');$('valeAvatar').classList.add('active');
      $('announcer').textContent=`Vale: ${s.vale}`;chirp('step');
    }else if(beat===1){
      beat=2;
      $('desk').classList.add('has-clue');$('clueContent').setAttribute('aria-hidden','false');
      $('kinetic').innerHTML=Motion.render(s,reduced());
      $('quinnAvatar').classList.remove('active');$('valeAvatar').classList.remove('active');
      $('announcer').textContent=`Clue, ${describeStatus(s).name.toLowerCase()}: ${s.clue}`;chirp('reveal');
    }else{
      if(idx===S.length-1){playing=false;paintPlay();goto(0);return;}
      goto(idx+1);return;
    }
    setAdvance();progress();if(playing)schedule();
  }
  function schedule(){
    clearTimeout(timer);if(!playing||document.hidden)return;
    const s=S[idx];const words=(beat===0?s.quinn:beat===1?s.vale:s.clue).split(/\s+/).length;
    const delay=Math.min(7900,Math.max(2700,words*185+1100))/speed;
    timer=setTimeout(()=>advance(),delay);
  }
  function paintPlay(){
    $('autoButton').innerHTML=playing?'❚❚ <span>PAUSE</span>':'▶ <span>AUTO</span>';
    $('autoButton').setAttribute('aria-pressed',String(playing));
  }
  function togglePlay(){playing=!playing;paintPlay();if(playing)schedule();else{clearTimeout(timer);timer=null;}}
  function toggleSound(){sound=!sound;$('soundButton').innerHTML=sound?'♫ <span>ON</span>':'♫ <span>OFF</span>';$('soundButton').setAttribute('aria-pressed',String(sound));if(sound)chirp('step');}
  function enter(index=idx){$('cover').hidden=true;$('story').hidden=false;window.scrollTo({top:0,behavior:reduced()?'instant':'smooth'});goto(index,{quiet:true});}
  function showCover(){playing=false;clearTimeout(timer);paintPlay();$('story').hidden=true;$('cover').hidden=false;try{window.history.replaceState(null,'',window.location.href.split('#')[0]);}catch(e){window.location.hash='';}window.scrollTo({top:0,behavior:reduced()?'instant':'smooth'});}
  function openOverlay(overlayId,html){
    lastFocus=document.activeElement;activeOverlay=overlayId;const overlay=$(overlayId);
    if(html!==undefined)$('modalBody').innerHTML=html;
    overlay.hidden=false;document.body.style.overflow='hidden';
    const modal=overlay.querySelector('.modal');modal.focus();
  }
  function closeOverlay(){
    if(!activeOverlay)return;$(activeOverlay).hidden=true;activeOverlay=null;document.body.style.overflow='';lastFocus?.focus?.();
  }
  function about(){
    openOverlay('infoOverlay',`<div class="eyebrow">BEFORE YOU BEGIN</div><h2>How to read this inquiry.</h2>
      <p>Quinn and Vale are fictional storytellers. This is an illustrated treatment of a <strong>proposed symbolic reading of golf</strong> and the historical questions it inspired. It is not a claim that the game was designed as a sexual ritual or that golf institutions were collectively involved in child sexual abuse.</p>
      <div class="fact-grid">
      <div class="legend"><strong>01 · HISTORICAL RECORD</strong><p>A sourced claim about dates, terminology, institutions, labor, or an individual documented case. A source may still require checking.</p></div>
      <div class="legend"><strong>02 · SYMBOLIC READING</strong><p>A metaphor or interpretation proposed for the game's equipment, movement, vocabulary or scoring.</p></div>
      <div class="legend"><strong>03 · RECORD + READING</strong><p>Real usage paired with a speculative inference. Those are distinct statements.</p></div>
      <div class="legend"><strong>04 · OPEN QUESTION</strong><p>An allegation, historical gap, or claim not established by the material collected so far.</p></div>
      </div><p><strong>Especially in Act IV and V:</strong> Documented young child labor, some residential camps, isolated later abuse cases, and some historical Masonic golf connections are distinct from a theory of organized trafficking. No evidence presented here establishes golf as a coordinated child-sex-trafficking institution or establishes criminal conduct by Freemasonry as an organization.</p>
      <p>This independent visual adaptation has no external analytics, trackers, fonts, or dependencies. Each scene offers a source link and an expanded note.</p>
      <button class="iconbtn primary" id="aboutDone">CONTINUE READING →</button>`);
    $('aboutDone').addEventListener('click',closeOverlay);
  }
  function sources(){
    const s=S[idx],info=describeStatus(s);
    const external=s.sourceUrl&&/^https:\/\//i.test(s.sourceUrl);
    openOverlay('infoOverlay',`<div class="eyebrow">FIELD NOTE ${String(idx+1).padStart(3,'0')} · ${clean(info.name)}</div>
      <h2>${clean(s.title)}</h2>
      <p><strong>The illustrated clue:</strong> ${clean(s.clue)}</p>
      <p>${clean(s.detail)}</p>
      <div class="legend"><strong>DOCUMENT OR REFERENCE</strong><p>${clean(s.sourceName||'Authoring dossier')}<br>${external?`<a class="src-link" href="${clean(s.sourceUrl)}" target="_blank" rel="noopener noreferrer">Open referenced material ↗</a>`:'A specific public source was not supplied.'}</p></div>
      <p style="font-size:12px;color:#61706c;margin-top:20px">Some references are contextual or secondary rather than direct citations for every sentence. Where the dossier flags unverified older archive leads, they are not treated as documented proof. This story is a research presentation, not a judicial or historical finding.</p>`);
  }
  function drawIndex(filter=''){
    const q=filter.toLowerCase().trim();const matching=S.filter(s=>!(q)&&true||[s.title,s.quinn,s.vale,s.act,s.detail].join(' ').toLowerCase().includes(q));
    $('indexGrid').innerHTML=matching.map(s=>`<button class="index-item" data-index="${s.number-1}" type="button"><span class="index-num">${String(s.number).padStart(2,'0')}</span><span>${clean(s.title)}<small>${clean(s.act)}</small></span></button>`).join('')||'<p>No scenes match. Try a different term.</p>';
    $('indexGrid').querySelectorAll('button[data-index]').forEach(b=>b.addEventListener('click',()=>{const i=+b.dataset.index;closeOverlay();enter(i);}));
  }
  function showIndex(){drawIndex();$('indexSearch').value='';openOverlay('indexOverlay');$('indexSearch').focus();}
  async function copyLink(){
    const text=sceneLink();const btn=$('copyLink');
    try{
      if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(text);}else{
        const t=document.createElement('textarea');t.value=text;t.style.position='fixed';t.style.left='-9999px';document.body.append(t);t.select();if(!document.execCommand('copy'))throw new Error('Copy blocked');t.remove();}
      btn.textContent='LINK COPIED ✓';setTimeout(()=>btn.textContent='SHARE THIS FRAME ↗',2100);
    }catch(e){btn.textContent='COPY UNAVAILABLE';setTimeout(()=>btn.textContent='SHARE THIS FRAME ↗',2200);}
  }
  function focusTrap(e){
    if(!activeOverlay||e.key!=='Tab')return;
    const d=$(activeOverlay),focusables=[...d.querySelectorAll('button:not([disabled]),input,[href],select,textarea,[tabindex]:not([tabindex="-1"])')].filter(el=>el.offsetParent!==null);
    if(!focusables.length)return;
    const first=focusables[0],last=focusables[focusables.length-1];
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
  }
  $('enterStory').addEventListener('click',()=>enter(0));
  $('tourActs').addEventListener('click',showIndex);
  $('advanceButton').addEventListener('click',advance);
  $('backButton').addEventListener('click',()=>{if(idx>0)goto(idx-1);});
  $('autoButton').addEventListener('click',togglePlay);
  $('speedButton').addEventListener('click',()=>{speed=({1:1.25,1.25:1.5,1.5:.75,.75:1})[speed]||1;$('speedButton').textContent=speed+'×';if(playing)schedule();});
  $('soundButton').addEventListener('click',toggleSound);
  $('fullscreenButton').addEventListener('click',()=>{if(document.fullscreenElement)document.exitFullscreen?.();else document.documentElement.requestFullscreen?.().catch(()=>{});});
  $('home').addEventListener('click',e=>{e.preventDefault();closeOverlay();showCover();});
  $('indexOpen').addEventListener('click',showIndex);
  $('aboutOpen').addEventListener('click',about);
  $('methodLink').addEventListener('click',e=>{e.preventDefault();about();});
  $('sourceOpen').addEventListener('click',sources);
  $('copyLink').addEventListener('click',copyLink);
  $('indexSearch').addEventListener('input',e=>drawIndex(e.target.value));
  $('actTimeline').querySelectorAll('[data-target]').forEach(b=>b.addEventListener('click',()=>goto(Number(b.dataset.target))));
  document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click',closeOverlay));
  for(const id of ['infoOverlay','indexOverlay'])$(id).addEventListener('mousedown',e=>{if(e.target===$(id))closeOverlay();});
  document.addEventListener('keydown',e=>{
    if(activeOverlay){focusTrap(e);if(e.key==='Escape'){e.preventDefault();closeOverlay();}return;}
    if(e.target instanceof HTMLElement && /^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName))return;
    if(e.key==='i'||e.key==='I'){e.preventDefault();showIndex();return;}
    if($('story').hidden)return;
    if(e.key===' '||e.key==='ArrowRight'||e.key==='Enter'&&e.target===document.body){e.preventDefault();advance();}
    else if(e.key==='ArrowLeft'){e.preventDefault();if(idx>0)goto(idx-1);}
    else if(e.key==='f'||e.key==='F'){$('fullscreenButton').click();}
    else if(e.key==='Escape'&&document.fullscreenElement){document.exitFullscreen?.();}
  });
  document.addEventListener('visibilitychange',()=>{if(document.hidden)clearTimeout(timer);else if(playing)schedule();});
  $('screen').addEventListener('touchstart',e=>{if(e.touches.length===1)touchStart={x:e.touches[0].clientX,y:e.touches[0].clientY};},{passive:true});
  $('screen').addEventListener('touchend',e=>{if(!touchStart||e.changedTouches.length!==1)return;const dx=e.changedTouches[0].clientX-touchStart.x;const dy=e.changedTouches[0].clientY-touchStart.y;touchStart=null;if(Math.abs(dx)>75&&Math.abs(dx)>Math.abs(dy)*1.5){if(dx<0)advance();else if(idx>0)goto(idx-1);}},{passive:true});
  window.addEventListener('hashchange',()=>{const m=window.location.hash.match(/^#scene=(\d+)$/);if(!m)return;const n=+m[1]-1;if(n>=0&&n<S.length&&n!==idx)enter(n);});
  const match=window.location.hash.match(/^#scene=(\d+)$/);
  if(match){const n=Number(match[1])-1;if(n>=0&&n<S.length)enter(n);}
  // No history update is needed on the cover; this also supports strict file:// origins.
})();
