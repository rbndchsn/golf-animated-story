(()=>{
  'use strict';
  const v=document.getElementById('film'),cta=document.getElementById('heroPlay'),status=document.getElementById('playHint'),grid=document.getElementById('chapterGrid'),download=document.getElementById('downloadFilm');
  let readyPromise=null,objectUrl=null;
  const chapters=[11.77,100.73,321.6,464.73,651.835];
  const motionReduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const scroll=()=>document.getElementById('film-player').scrollIntoView({behavior:motionReduced?'instant':'smooth'});
  async function prepare(){
    if(readyPromise)return readyPromise;
    readyPromise=(async()=>{
      status.textContent='Loading the complete film. Please wait...';
      const response=await fetch('film/film_manifest.json',{cache:'force-cache'});
      if(!response.ok)throw Error('Film manifest unavailable');
      const manifest=await response.json();
      const n=manifest.chunks.length;
      let completed=0;
      const chunks=await Promise.all(manifest.chunks.map(async (part)=>{
        const resp=await fetch(part.path,{cache:'force-cache'});
        if(!resp.ok)throw Error('A movie segment could not be fetched');
        const bytes=await resp.arrayBuffer();
        if(bytes.byteLength!==part.bytes)throw Error('Movie segment size mismatch');
        completed++;
        status.textContent=`Loading movie: ${completed} of ${n} parts received...`;
        return bytes;
      }));
      if(chunks.reduce((sum,c)=>sum+c.byteLength,0)!==manifest.bytes)throw Error('The movie is incomplete');
      // Reconstruct the original MP4 byte-for-byte; viewers get a single continuous video.
      const movie=new Blob(chunks,{type:'video/mp4'});
      objectUrl=URL.createObjectURL(movie);
      v.src=objectUrl;
      v.load();
      await new Promise((resolve,reject)=>{
        if(v.readyState>=1){resolve();return}
        v.addEventListener('loadedmetadata',resolve,{once:true});
        v.addEventListener('error',()=>reject(Error('Browser cannot load this MP4')),{once:true});
      });
      status.textContent='Ready: the entire 12:43 video is loaded. Press Play to watch.';
      download.disabled=false;
      return objectUrl;
    })().catch(e=>{
      status.textContent='Unable to prepare the video: '+e.message;
      cta.disabled=false;
      readyPromise=null;
      throw e;
    });
    return readyPromise;
  }
  async function playAt(time){
    scroll();
    try{
      cta.disabled=true;
      await prepare();
      if(typeof time==='number')v.currentTime=time;
      await v.play();
      status.textContent='Playing the complete 43-scene film.';
    }catch(e){status.textContent='Film ready. If playback was blocked by the browser, press Play on the video.'}
    finally{cta.disabled=false}
  }
  cta.addEventListener('click',()=>playAt());
  grid.querySelectorAll('.chapter').forEach((b,i)=>b.addEventListener('click',()=>playAt(chapters[i])));
  download.disabled=true;
  download.addEventListener('click',async()=>{
    try{
      const link=await prepare();
      const a=document.createElement('a');a.href=link;a.download='The_Game_Beneath_The_Game_Full_Film.mp4';
      document.body.appendChild(a);a.click();a.remove();
    }catch(e){status.textContent='Could not download the film: '+e.message}
  });
  v.addEventListener('ended',()=>status.textContent='Film complete. Explore each source and interpretation in the interactive exhibit.');
  // Begin loading before the viewer presses Play, so autoplay-after-click is more reliable.
  prepare().catch(()=>{});
})();
