// Contact API URL. Pages rendered by Django set <body data-api="/api/contact/">.
// For the static GitHub Pages copy, set this to your deployed backend (e.g. 'https://infinitecare.onrender.com/api/contact/');
// when empty and no data-api is present the form falls back to a mailto: link.
const API_URL = '';
(()=>{const b=document.body,nav=document.querySelector('.nav'),prog=document.querySelector('.progress');
addEventListener('load',()=>setTimeout(()=>b.classList.add('loaded'),200));setTimeout(()=>b.classList.add('loaded'),1800);
addEventListener('pageshow',e=>{if(e.persisted)b.classList.remove('leaving')});
// page transitions (internal links to another page)
document.querySelectorAll('a[href]').forEach(a=>a.addEventListener('click',e=>{if(e.metaKey||e.ctrlKey||e.shiftKey||a.target)return;const h=a.getAttribute('href');if(!h||h[0]==='#'||/^(tel|mailto):/.test(h))return;const u=new URL(a.href,location.href);if(u.origin!==location.origin||(u.pathname===location.pathname&&u.hash))return;e.preventDefault();b.classList.remove('menu-open');b.classList.add('leaving');setTimeout(()=>location.href=u.href,650)}));
// mobile menu
document.querySelector('.burger').onclick=()=>b.classList.toggle('menu-open');
// split headings into words
document.querySelectorAll('.split').forEach(h=>{const walk=n=>[...n.childNodes].forEach(c=>{if(c.nodeType===3){const f=document.createDocumentFragment();c.textContent.split(/(\s+)/).forEach(w=>{if(!w)return;if(/^\s+$/.test(w)){f.append(' ');return}const o=document.createElement('span');o.className='w';const i=document.createElement('span');i.textContent=w;o.append(i);f.append(o)});c.replaceWith(f)}else if(c.nodeType===1&&c.tagName!=='BR')walk(c)});walk(h);h.querySelectorAll('.w>span').forEach((s,i)=>s.style.transitionDelay=i*60+'ms')});
// reveal on scroll
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);if(e.target.dataset.count!==undefined)count(e.target)}}),{threshold:.15,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.reveal,.reveal-img,.split,[data-count]').forEach((el,i)=>{if(el.classList.contains('reveal')){const sib=[...el.parentElement.children].filter(x=>x.classList.contains('reveal'));el.style.transitionDelay=Math.min(sib.indexOf(el),5)*110+'ms'}io.observe(el)});
const hero=document.querySelector('.hero h1');if(hero)setTimeout(()=>hero.classList.add('in'),900);
function count(el){const t=+el.dataset.count,s=performance.now();const f=n=>{const p=Math.min((n-s)/1800,1);el.textContent=Math.round(t*(1-Math.pow(1-p,4)))+(p===1?(el.dataset.suffix??''):'');if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}
// scroll: nav, progress, parallax
const px=[...document.querySelectorAll('[data-parallax]')];
let tick=0;
const run=()=>{tick=0;const y=scrollY,vh=innerHeight,max=document.documentElement.scrollHeight-vh,rs=px.map(el=>el.parentElement.getBoundingClientRect()); // all layout reads first, then the writes
 nav.classList.toggle('scrolled',y>60);prog.style.width=(max>0?y/max*100:0)+'%';px.forEach((el,i)=>{const r=rs[i];if(r.bottom>0&&r.top<vh)el.style.transform=`translate3d(0,${r.top*-.18}px,0)`})};
const onS=()=>{if(!tick){tick=1;requestAnimationFrame(run)}};
addEventListener('scroll',onS,{passive:true});onS();
// tilt + cursor glow (pointer devices)
if(matchMedia('(hover:hover)').matches){const g=document.querySelector('.cursor-glow');addEventListener('mousemove',e=>{g.style.left=e.clientX+'px';g.style.top=e.clientY+'px'});
document.querySelectorAll('[data-tilt]').forEach(el=>{const t=el.closest('.f-img')||el;t.addEventListener('mousemove',e=>{const r=t.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;t.style.transform=`perspective(900px) rotateY(${x*6}deg) rotateX(${-y*6}deg)`});t.addEventListener('mouseleave',()=>t.style.transform='')})}

// gallery: filters + lightbox, reels
const gg=document.querySelector('.g-grid');
if(gg){const items=[...gg.querySelectorAll('.g-item')],fb=[...document.querySelectorAll('.g-filters button')];
 const vis=()=>items.filter(i=>!i.hidden);
 fb.forEach(x=>x.addEventListener('click',()=>{fb.forEach(y=>{y.classList.toggle('on',y===x);y.setAttribute('aria-pressed',y===x)});items.forEach(i=>{i.hidden=x.dataset.filter!=='all'&&i.dataset.cat!==x.dataset.filter})}));
 let lb,cur=-1,last;
 const build=()=>{lb=document.createElement('div');lb.className='lb';lb.setAttribute('role','dialog');lb.setAttribute('aria-modal','true');lb.hidden=true;
  lb.innerHTML='<button type="button" class="lb-x"></button><button type="button" class="lb-p"></button><button type="button" class="lb-n"></button><figure><img alt=""><figcaption></figcaption></figure>';
  lb.querySelector('.lb-x').setAttribute('aria-label',gg.dataset.lbClose);lb.querySelector('.lb-p').setAttribute('aria-label',gg.dataset.lbPrev);lb.querySelector('.lb-n').setAttribute('aria-label',gg.dataset.lbNext);
  lb.addEventListener('click',e=>{if(e.target===lb)close();else if(e.target.closest('.lb-x'))close();else if(e.target.closest('.lb-p'))go(-1);else if(e.target.closest('.lb-n'))go(1)});
  let sx=0;lb.addEventListener('touchstart',e=>sx=e.touches[0].clientX,{passive:true});lb.addEventListener('touchend',e=>{const d=e.changedTouches[0].clientX-sx;if(Math.abs(d)>50)go(d<0?1:-1)});
  document.body.append(lb)};
 const show=()=>{const v=vis(),it=v[cur];lb.querySelector('img').src=it.dataset.full;lb.querySelector('img').alt=it.dataset.caption;lb.querySelector('figcaption').textContent=it.dataset.caption;lb.classList.toggle('single',v.length<2)};
 const go=d=>{const n=vis().length;cur=(cur+d+n)%n;show()};
 const open=it=>{if(!lb)build();last=it;cur=vis().indexOf(it);show();lb.hidden=false;b.classList.add('lb-open');lb.querySelector('.lb-x').focus()};
 const close=()=>{lb.hidden=true;b.classList.remove('lb-open');if(last)last.focus()};
 items.forEach(i=>i.addEventListener('click',()=>open(i)));
 addEventListener('keydown',e=>{if(!lb||lb.hidden)return;if(e.key==='Escape')close();else if(e.key==='ArrowLeft')go(-1);else if(e.key==='ArrowRight')go(1)})}
const reels=[...document.querySelectorAll('[data-reel]')];
if(reels.length){const still=matchMedia('(prefers-reduced-motion:reduce)').matches;
 const vo=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(still)return;if(e.isIntersecting){v.preload='auto';v.play().catch(()=>{})}else v.pause()}),{threshold:.5});
 reels.forEach(v=>{if(!still)vo.observe(v);const bt=v.parentElement.querySelector('.reel-btn');
  const sync=()=>v.parentElement.classList.toggle('paused',v.paused);v.addEventListener('play',sync);v.addEventListener('pause',sync);sync();
  bt.addEventListener('click',()=>{v.paused?v.play().catch(()=>{}):v.pause()})})}

// map: load Google Maps only after a click (no third-party requests/cookies on page load)
document.querySelectorAll('[data-map]').forEach(w=>{const bt=w.querySelector('.map-btn');if(!bt)return;
 bt.addEventListener('click',()=>{const f=document.createElement('iframe');f.src=w.dataset.map;f.title=w.dataset.title;f.referrerPolicy='no-referrer-when-downgrade';f.allowFullscreen=true;w.replaceChildren(f);f.focus()})});

// language: remember choice, redirect first visit of a session
const lang=b.dataset.lang;
document.querySelectorAll('.langsw a').forEach(a=>a.addEventListener('click',()=>{try{localStorage.setItem('ic-lang',a.dataset.lang)}catch(e){}document.cookie='ic-lang='+a.dataset.lang+';path=/;max-age=31536000;samesite=lax'}));
try{const saved=localStorage.getItem('ic-lang');const internal=document.referrer&&new URL(document.referrer).origin===location.origin;
 if(saved&&saved!==lang&&!internal){const a=document.querySelector(`.langsw a[data-lang="${saved}"]`);if(a&&a.getAttribute('href')!=='#'){location.replace(a.href);return}}}catch(e){}
// contact form
const form=document.getElementById('contact-form');
if(form){const st=form.querySelector('.form-status'),btn=form.querySelector('button');
 const show=(m,c)=>{st.textContent=m;st.className='form-status '+c};
 const mailto=d=>{location.href='mailto:'+(form.dataset.mailto||'info@infinitecare.hu')+'?subject='+encodeURIComponent('Infinite Care – '+d.name)+'&body='+encodeURIComponent(d.message+'\n\n'+d.name+'\n'+d.email+(d.phone?'\n'+d.phone:''))};
 form.addEventListener('submit',async e=>{e.preventDefault();
  let ok=true;form.querySelectorAll('[required]').forEach(i=>{const v=i.checkValidity()&&i.value.trim();i.parentElement.classList.toggle('invalid',!v);if(!v)ok=false});
  if(!ok){show(form.dataset.invalid,'err');return}
  const d=Object.fromEntries(new FormData(form));d.lang=lang;const api=b.dataset.api||API_URL;if(!api){mailto(d);return}
  const label=btn.textContent;btn.disabled=true;btn.textContent=form.dataset.sending;
  try{const ctl=new AbortController();const to=setTimeout(()=>ctl.abort(),10000);
   const r=await fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d),signal:ctl.signal});clearTimeout(to);
   const ct=r.headers.get('content-type')||'';
   if(!ct.includes('application/json')){mailto(d);return} // no backend (e.g. GitHub Pages)
   if(r.ok){show(form.dataset.ok,'ok');form.reset()}else show(r.status===422?form.dataset.invalid:form.dataset.err,'err');
  }catch(err){mailto(d)}finally{btn.disabled=false;btn.textContent=label}})}
})();
