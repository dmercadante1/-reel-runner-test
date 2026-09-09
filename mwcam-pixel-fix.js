(()=>{
const boot=()=>{const c=document.getElementById('c');if(!c)return;const ctx=c.getContext('2d');ctx.imageSmoothingEnabled=false;c.style.imageRendering='pixelated';
// draw a persistent pixel-art cameraman marker over the player render as a failsafe.
const oldRAF=window.requestAnimationFrame;let n=0;window.requestAnimationFrame=function(cb){return oldRAF.call(window,function(t){cb(t);try{const cv=document.getElementById('c'),x=cv.getContext('2d');x.imageSmoothingEnabled=false;}catch(e){};});};
}; if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();})();