// Live content: pages are static HTML (SEO, first paint) and, in the browser, the parts the admin can edit are checked against
// the JSON API (body[data-api] without /api/contact/) and swapped only when they differ - see the "live content" section at the bottom.
// Contact API URL. Pages rendered by Django set <body data-api="/api/contact/">.
// The Cloudflare site posts to the Django API Worker (scripts/sync_from_api.sh) and falls back to its own /api/contact/.
// For the static GitHub Pages copy, set this to your deployed backend (e.g. 'https://infinitecare.onrender.com/api/contact/');
// when empty and no data-api is present the form falls back to a mailto: link.
const API_URL = '';
(()=>{const b=document.body,nav=document.querySelector('.nav'),prog=document.querySelector('.progress');
addEventListener('load',()=>setTimeout(()=>b.classList.add('loaded'),200));setTimeout(()=>b.classList.add('loaded'),1800);
addEventListener('pageshow',e=>{if(e.persisted)b.classList.remove('leaving')});
// page transitions (internal links to another page)
document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[href]');if(!a||e.defaultPrevented||e.button||e.metaKey||e.ctrlKey||e.shiftKey||a.target)return;const h=a.getAttribute('href');if(!h||h[0]==='#'||/^(tel|mailto):/.test(h))return;const u=new URL(a.href,location.href);if(u.origin!==location.origin||(u.pathname===location.pathname&&u.hash))return;e.preventDefault();b.classList.remove('menu-open');b.classList.add('leaving');setTimeout(()=>location.href=u.href,650)});
// mobile menu
document.querySelector('.burger').onclick=()=>b.classList.toggle('menu-open');
// split headings into words
const splitEl=h=>{const walk=n=>[...n.childNodes].forEach(c=>{if(c.nodeType===3){const f=document.createDocumentFragment();c.textContent.split(/(\s+)/).forEach(w=>{if(!w)return;if(/^\s+$/.test(w)){f.append(' ');return}const o=document.createElement('span');o.className='w';const i=document.createElement('span');i.textContent=w;o.append(i);f.append(o)});c.replaceWith(f)}else if(c.nodeType===1&&c.tagName!=='BR')walk(c)});walk(h);h.querySelectorAll('.w>span').forEach((s,i)=>s.style.transitionDelay=i*60+'ms')};
document.querySelectorAll('.split').forEach(splitEl);
// reveal on scroll
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);if(e.target.dataset.count!==undefined)count(e.target)}}),{threshold:.15,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.reveal,.reveal-img,.split,[data-count]').forEach((el,i)=>{if(el.classList.contains('reveal')){const sib=[...el.parentElement.children].filter(x=>x.classList.contains('reveal'));el.style.transitionDelay=Math.min(sib.indexOf(el),5)*110+'ms'}io.observe(el)});
const hero=document.querySelector('.hero h1');if(hero)setTimeout(()=>hero.classList.add('in'),900);
function count(el){const t=+el.dataset.count,s=performance.now();const f=n=>{const p=Math.min((n-s)/1800,1);el.textContent=Math.round(t*(1-Math.pow(1-p,4)))+(p===1?(el.dataset.suffix??''):'');if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}
// scroll: nav, progress, parallax
let px=[...document.querySelectorAll('[data-parallax]')];const refreshPx=()=>{px=[...document.querySelectorAll('[data-parallax]')];onS()};
let tick=0;
const run=()=>{tick=0;const y=scrollY,vh=innerHeight,max=document.documentElement.scrollHeight-vh,rs=px.map(el=>el.parentElement.getBoundingClientRect()); // all layout reads first, then the writes
 nav.classList.toggle('scrolled',y>60);prog.style.width=(max>0?y/max*100:0)+'%';px.forEach((el,i)=>{const r=rs[i];if(r.bottom>0&&r.top<vh)el.style.transform=`translate3d(0,${r.top*-.18}px,0)`})};
const onS=()=>{if(!tick){tick=1;requestAnimationFrame(run)}};
addEventListener('scroll',onS,{passive:true});onS();
// tilt + cursor glow (pointer devices)
const hov=matchMedia('(hover:hover)').matches;
if(hov){const g=document.querySelector('.cursor-glow');addEventListener('mousemove',e=>{g.style.left=e.clientX+'px';g.style.top=e.clientY+'px'})}
const initTilt=root=>{if(!hov)return;root.querySelectorAll('[data-tilt]').forEach(el=>{if(el.dataset.tb)return;el.dataset.tb=1;const t=el.closest('.f-img')||el;t.addEventListener('mousemove',e=>{const r=t.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;t.style.transform=`perspective(900px) rotateY(${x*6}deg) rotateX(${-y*6}deg)`});t.addEventListener('mouseleave',()=>t.style.transform='')})};
initTilt(document);

// gallery: filters + lightbox (delegated, so the grid can be re-rendered live)
const gg=document.querySelector('.g-grid'),gf=document.querySelector('.g-filters');let setFilter=()=>{},curFilter='all';
if(gg){const photos=()=>[...gg.querySelectorAll('.g-item:not(.g-vid)')],vis=()=>photos().filter(i=>!i.hidden);
 setFilter=k=>{curFilter=k;const bs=[...gf.querySelectorAll('button')];bs.forEach(y=>{const on=y.dataset.filter===k;y.classList.toggle('on',on);y.setAttribute('aria-pressed',on)});gg.querySelectorAll('.g-item').forEach(i=>{i.hidden=k!=='all'&&!i.dataset.cat.split(' ').includes(k)});const st=document.querySelector('.g-status');if(st)st.textContent=st.dataset.tpl.replace('{n}',[...gg.querySelectorAll('.g-item')].filter(i=>!i.hidden).length)};
 if(gf)gf.addEventListener('click',e=>{const x=e.target.closest('button');if(!x)return;setFilter(x.dataset.filter);const bar=x.parentElement;if(bar.scrollWidth>bar.clientWidth)bar.scrollTo({left:x.offsetLeft-bar.offsetLeft-12,behavior:'smooth'})});
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
 gg.addEventListener('click',e=>{const it=e.target.closest('.g-item:not(.g-vid)');if(it&&gg.contains(it))open(it)});
 addEventListener('keydown',e=>{if(!lb||lb.hidden)return;if(e.key==='Escape')close();else if(e.key==='ArrowLeft')go(-1);else if(e.key==='ArrowRight')go(1)})}
const still=matchMedia('(prefers-reduced-motion:reduce)').matches;
const vo=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(still)return;if(e.isIntersecting){v.preload='auto';v.play().catch(()=>{})}else v.pause()}),{threshold:.5});
const initReels=root=>root.querySelectorAll('[data-reel]').forEach(v=>{if(v.dataset.rb)return;v.dataset.rb=1;if(!still)vo.observe(v);const bt=v.parentElement.querySelector('.reel-btn');
  const sync=()=>v.parentElement.classList.toggle('paused',v.paused);v.addEventListener('play',sync);v.addEventListener('pause',sync);sync();
  bt.addEventListener('click',()=>{v.paused?v.play().catch(()=>{}):v.pause()})});
initReels(document);

// YouTube: the poster is ours; the player (youtube-nocookie.com) is only added after a click
const initYT=root=>root.querySelectorAll('.yt[data-yt]').forEach(w=>{if(w.dataset.yb)return;w.dataset.yb=1;const bt=w.querySelector('.yt-btn');
 bt.addEventListener('click',()=>{const f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+w.dataset.yt+'?autoplay=1&rel=0&playsinline=1&hl='+b.dataset.lang;f.title=w.dataset.title;f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;f.referrerPolicy='strict-origin-when-cross-origin';bt.replaceWith(f);f.focus()})});
initYT(document);

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
  // the form posts to the Django API (other origin); if that is unreachable / failing, the same-origin Worker endpoint takes the message
  const fb=/^https?:/.test(api)&&!api.startsWith(location.origin+'/')&&/^https?:/.test(location.origin);
  const post=async u=>{const ctl=new AbortController();const to=setTimeout(()=>ctl.abort(),10000);
   try{return await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d),signal:ctl.signal})}finally{clearTimeout(to)}};
  try{let r;
   try{r=await post(api);if(fb&&r.status>=500)throw 0}catch(e){if(!fb)throw e;r=await post('/api/contact/')}
   const ct=r.headers.get('content-type')||'';
   if(!ct.includes('application/json')){mailto(d);return} // no backend (e.g. GitHub Pages)
   if(r.ok){show(form.dataset.ok,'ok');form.reset()}else show(r.status===422?form.dataset.invalid:form.dataset.err,'err');
  }catch(err){mailto(d)}finally{btn.disabled=false;btn.textContent=label}})}

// ---- live content ----------------------------------------------------------------------------------------------------
// The HTML is exported from the admin API at build time (SEO, first paint, no-JS). After load this checks the same API
// from the browser and re-renders ONLY what changed, so admin edits show without a rebuild/redeploy. Every editable
// section carries data-fp (fingerprint of the data it was built from); scalar settings use data-s bindings.
// Fails silently (4 s timeout, any error): the static content simply stays. Keep fp() identical to backend/content/live.py.
{
const api=(b.dataset.api||'').replace(/\/api\/contact\/?$/,'').replace(/\/+$/,'');
if(/^https?:\/\//.test(api)&&window.fetch){
const hu=b.dataset.lang==='hu';
const root=b.dataset.root||'',svcId=b.dataset.svc||'';
const slug=b.dataset.slug||(b.hasAttribute('data-shell')&&new URLSearchParams(location.search).get('p'))||'';
const L=hu?{more:'Bővebben a kezelésről',vids:'Nézd meg a kezelést',read:'Tovább olvasom →',nt:'új lapon nyílik meg',bo:'Online időpontfoglalás',bk:'Foglalás',play:'Videó lejátszása',empty:'Hamarosan új cikkekkel jelentkezünk.',reel:'Videó lejátszása / szüneteltetése',offers:'Akciók',
 f:{all:'Mind',clinic:'Klinika',treatments:'Kezelések',events:'Események',whitening:'Fogfehérítés',facial:'Arckezelés',laser:'Lézer',emsculpt:'Emsculpt',carbon:'Carbon hámlasztás',cellulite:'Cellulit',brazilift:'Brazilift'}}
 :{more:'More about this treatment',vids:'Watch the treatment',read:'Read more →',nt:'opens in a new tab',bo:'Book online',bk:'Book an appointment',play:'Play video',empty:'New articles are coming soon.',reel:'Play / pause video',offers:'Offers',
 f:{all:'All',clinic:'Clinic',treatments:'Treatments',events:'Events',whitening:'Teeth Whitening',facial:'Facial',laser:'Laser',emsculpt:'Emsculpt',carbon:'Carbon Peeling',cellulite:'Cellulite',brazilift:'Brazilift'}};
const q=(s,r=document)=>[...r.querySelectorAll(s)];
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const faqMark=bl=>{let f=0;return (bl||[]).map(k=>{if(k.type!=='h')return k;const t=String(k.text||'').trimEnd();if(/^\s*(frequently asked questions|gyakran ism[eé]telt k[eé]rd[eé]sek|faq)\b/i.test(t)){f=1;return k}if(f&&t.endsWith('?'))return {...k,type:'q'};f=0;return k})};
const linkify=t=>{t=String(t);let o='',p=0;const re=/\[([^\]\n]{1,200})\]\(((?:https?:\/\/|\/)[^\s()<>"]*)\)|(https?:\/\/[^\s<>"]+[^\s<>".,;:!?)])/g;let m;while((m=re.exec(t))){o+=esc(t.slice(p,m.index));const l=m[2]?m[1]:m[3],u=m[2]||m[3],x=/^http/.test(u)&&!u.startsWith('https://www.infinitecare.hu');o+='<a href="'+esc(u)+'"'+(x?' target="_blank" rel="noopener"':'')+'>'+esc(l)+'</a>';p=re.lastIndex}return o+esc(t.slice(p))};
const brk=s=>esc(s).replace(/\r?\n/g,'<br>');
const MEDIA=api+'/media/';
const dec=s=>{try{return decodeURIComponent(s)}catch(e){return s}};
const norm=u=>{u=String(u==null?'':u);if(u.startsWith(MEDIA))return '~/'+dec(u.slice(MEDIA.length));const m=u.match(/^(?:\.\.\/)*assets\/media\/(.+)$/);return m?'~/'+m[1]:u};
const canon=o=>typeof o==='string'?norm(o):Array.isArray(o)?o.map(canon):o&&typeof o==='object'?Object.keys(o).sort().reduce((r,k)=>(r[k]=canon(o[k]),r),{}):o;
const ser=o=>Array.isArray(o)?'['+o.map(ser).join(',')+']':o&&typeof o==='object'?'{'+Object.keys(o).sort().map(k=>JSON.stringify(k)+':'+ser(o[k])).join(',')+'}':JSON.stringify(o);
const fp=o=>{const s=ser(canon(o)).replace(/[\u007f-\uffff]/g,c=>'\\u'+('000'+c.charCodeAt(0).toString(16)).slice(-4));let h=0x811c9dc5;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0}return h.toString(16)+'-'+s.length};

// fetch with a short cache (sessionStorage, 60 s) and stale-while-revalidate; cb(data,status) may run twice
const nourl=o=>Array.isArray(o)?o.map(nourl):Object.keys(o).filter(k=>k!=='url').reduce((r,k)=>(r[k]=o[k],r),{});   // API urls are Django paths; the static layout has its own
const D={};let busy={};
const J=(key,path)=>{const url=api+path+'?lang='+b.dataset.lang,ck='ic:'+url;let c;
 try{c=JSON.parse(sessionStorage.getItem(ck))}catch(e){}
 if(c&&c.d){D[key]={d:c.d,s:c.s}}
 if(c&&Date.now()-c.t<6e4)return Promise.resolve();
 const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),4000);
 return fetch(url,{signal:ctl.signal,headers:{Accept:'application/json'}}).then(r=>{if(!(r.headers.get('content-type')||'').includes('json'))throw 0;return r.json().then(d=>{if(r.ok||r.status===404){D[key]={d,s:r.status};try{sessionStorage.setItem(ck,JSON.stringify({t:Date.now(),d,s:r.status}))}catch(e){}}})}).catch(()=>{}).finally(()=>clearTimeout(to))};
const ok=(k,t)=>D[k]&&D[k].s===200&&D[k].d&&t(D[k].d)?D[k].d:null;

// helpers
const tpl=h=>{const t=document.createElement('template');t.innerHTML=h;return t.content};
const sized=root=>Promise.all(q('img[src]',root).filter(i=>!i.getAttribute('width')).map(i=>new Promise(r=>{const p=new Image(),t=setTimeout(()=>r(false),5000);
 p.onload=()=>{clearTimeout(t);if(p.naturalWidth){i.setAttribute('width',p.naturalWidth);i.setAttribute('height',p.naturalHeight)}r(true)};p.onerror=()=>{clearTimeout(t);r(false)};p.src=i.getAttribute('src')}))).then(a=>a.every(Boolean));
const swapImg=(img,url)=>{if(!img||!url||norm(img.getAttribute('src'))===norm(url))return Promise.resolve(true);
 return new Promise(r=>{const p=new Image(),t=setTimeout(()=>r(false),5000);p.onload=()=>{clearTimeout(t);img.removeAttribute('srcset');img.src=url;if(p.naturalWidth){img.setAttribute('width',p.naturalWidth);img.setAttribute('height',p.naturalHeight)}r(true)};p.onerror=()=>{clearTimeout(t);r(false)};p.src=url})};
const txt=(el,v)=>{if(el&&el.textContent!==String(v==null?'':v))el.textContent=v};
const attr=(el,n,v)=>{if(el&&el.getAttribute(n)!==v)el.setAttribute(n,v)};
const show=(el,on)=>{if(el&&el.hidden===on)el.hidden=!on};
const flat=s=>s.replace(/\s+/g,'');
const heading=(h,main,em)=>{if(!h||flat(h.textContent)===flat(main+(em||'')))return;h.innerHTML=esc(main)+(em?'<br><em>'+esc(em)+'</em>':'');splitEl(h);h.classList.add('in')};
const settle=el=>{if(el.classList)el.classList.add('in');q('.reveal,.reveal-img,.split',el).forEach(x=>x.classList.add('in'));q('.split',el).forEach(h=>{if(!h.querySelector('.w'))splitEl(h)});initTilt(el);initYT(el);initReels(el);refreshPx()};
const upd=(key,f,fn)=>{const el=document.querySelector('[data-live="'+key+'"]');if(!el||el.dataset.fp===f||busy[key]===f)return;busy[key]=f;
 Promise.resolve().then(()=>fn(el)).then(r=>{if(r!==false)el.dataset.fp=f}).catch(()=>{}).then(()=>{if(busy[key]===f)delete busy[key]})};
const replace=(el,html,f)=>{const n=tpl(html).firstElementChild;n.dataset.fp=f;return sized(n).then(g=>{if(!g)return false;el.replaceWith(n);settle(n)})};

// templates (same markup as backend/templates/site/*.html)
const yt=v=>`<div class="yt ${v.vertical?'yt-v':'yt-w'}" data-yt="${esc(v.youtube_id)}" data-title="${esc(v.title)}"><button type="button" class="yt-btn" aria-label="${esc(L.play)}: ${esc(v.title)}"><img src="${esc(v.poster)}" alt="" width="${esc(v.width)}" height="${esc(v.height)}" loading="lazy" decoding="async"><strong class="yt-t">${esc(v.title)}</strong></button>${v.caption?'<small class="yt-c">'+esc(v.caption)+'</small>':''}</div>`;
const bookA=(label,cls,u)=>`<a class="btn ${cls}" href="${esc(u)}" target="_blank" rel="noopener noreferrer" data-s="booking">${esc(label)}<span class="vh"> (${esc(L.nt)})</span></a>`;
const navA=i=>q('.menu>a')[i];
const feature=(f,rev,href,key,fpv)=>`<section class="feature ${rev?'feature-rev':''} wrap" data-live="${key}" data-fp="${fpv}"><div class="f-img reveal-img in"><img src="${esc(f.image)}" alt="${esc(f.title)}" loading="lazy" decoding="async" data-tilt></div><div class="f-text"><span class="eyebrow reveal in">${esc(f.eyebrow)}</span><h2 class="split in">${esc(f.title)}</h2>${f.paragraphs.map(p=>'<p class="reveal in">'+brk(p)+'</p>').join('')}${f.button?'<a class="btn reveal in" href="'+esc(href)+'">'+esc(f.button)+'</a>':''}</div></section>`;
const known=(b.dataset.slugs||'').split(',');
const card=p=>{const u=esc(known.includes(p.slug)?b.dataset.post.replace('__SLUG__',p.slug):b.dataset.post.replace('__SLUG__','post')+'?p='+encodeURIComponent(p.slug));return `<article class="bcard reveal in"><a class="bc-img" href="${u}" tabindex="-1" aria-hidden="true"><img src="${esc(p.cover)}" alt="" loading="lazy" decoding="async"></a><div class="bc-body"><time datetime="${esc(p.iso_date)}">${esc(p.date)}</time><h3><a href="${u}">${esc(p.title)}</a></h3><p>${esc(p.excerpt)}</p><a class="bc-more" href="${u}">${esc(L.read)}</a></div></article>`};

// settings: contact data, booking/offers/social links (idempotent bindings, no layout change unless a value changed)
const bind=s=>{
 q('[data-s=phone]').forEach(a=>{txt(a,s.phone);if(a.tagName==='A')attr(a,'href',s.phone_href)});
 q('[data-s=tel]').forEach(a=>attr(a,'href',s.phone_href));
 q('[data-s=email]').forEach(a=>{txt(a,s.email);attr(a,'href','mailto:'+s.email)});
 q('[data-s=address]').forEach(e=>txt(e,s.address));q('[data-s=city]').forEach(e=>txt(e,s.city));q('[data-s=tagline]').forEach(e=>txt(e,s.tagline));
 q('[data-s=addrcity]').forEach(e=>txt(e,s.address+', '+s.city));
 q('[data-s=maplink]').forEach(a=>attr(a,'href','https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(s.address)+'%2C%20'+encodeURIComponent(s.city)));
 q('[data-s=mailto]').forEach(f=>{f.dataset.mailto=s.email});
 q('[data-s=hours]').forEach(p=>{const cur=[...p.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent).join('\n');if(cur===s.hours.join('\n'))return;p.replaceChildren(...s.hours.flatMap((l,i)=>i?[document.createElement('br'),document.createTextNode(l)]:[document.createTextNode(l)]))});
 q('[data-s=map]').forEach(m=>{if(m.dataset.map!==s.map_embed)m.dataset.map=s.map_embed;show(m,!!s.map_embed)});
 q('[data-s=booking]').forEach(a=>{const on=!!s.booking_url;if(on)attr(a,'href',s.booking_url);show(a,on);const w=a.closest('.bookband,.c-book');if(w)show(w,on)});
 const off=q('[data-s=offers]');
 if(s.offers_url&&!off.length){const sw=document.querySelector('.menu .langsw'),p=sw&&sw.previousElementSibling;if(p){const a=document.createElement('a');a.href=s.offers_url;a.target='_blank';a.rel='noopener noreferrer';a.dataset.s='offers';a.append(L.offers);const v=document.createElement('span');v.className='vh';v.textContent=' ('+L.nt+')';a.append(v);p.before(a)}}
 else off.forEach(a=>{if(s.offers_url)attr(a,'href',s.offers_url);show(a,!!s.offers_url)});
 ['facebook','instagram','youtube','tiktok'].forEach(k=>q('[data-s=soc-'+k+']').forEach(a=>{if(s[k])attr(a,'href',s[k]);show(a,!!s[k])}));
 q('.c-social').forEach(w=>show(w,q('[data-s^=soc-]',w).some(a=>!a.hidden)));
 q('.watch .w-text a.btn[rel~=me]').forEach(a=>{if(s.youtube)attr(a,'href',s.youtube)});
};

const render=()=>{
 const S=ok('settings',d=>d.phone!==undefined&&Array.isArray(d.hours));
 const H=ok('home',d=>d.f1&&d.f2&&Array.isArray(d.counters)&&Array.isArray(d.marquee)),G=ok('gallery',d=>Array.isArray(d.photos)&&Array.isArray(d.youtube)&&Array.isArray(d.videos));
 const SV=ok('services',d=>Array.isArray(d.results)),B=ok('blog',d=>Array.isArray(d.results)),P=ok('post',d=>Array.isArray(d.blocks)&&d.slug);
 if(S)bind(S);
 if(H){
  upd('hero',fp([H.hero_image,H.hello,H.h1_main,H.h1_em,H.lead]),el=>{const i=el.querySelector('.hero-bg img');txt(el.querySelector('.hero-script'),H.hello);heading(el.querySelector('h1'),H.h1_main,H.h1_em);txt(el.querySelector('.lead'),H.lead);return swapImg(i,H.hero_image)});
  upd('marquee',fp(H.marquee),el=>{const w=H.marquee;show(el,!!w.length);const t=el.querySelector('.marquee-track'),s=w.concat(w).map(x=>`<span>${esc(x)}</span><i>✦</i>`).join('');if(s)t.innerHTML=s});
  [['f1',false],['f2',true]].forEach(([k,rev])=>upd(k,fp(H[k]),el=>{const a=el.querySelector('a.btn'),h=a?a.getAttribute('href'):navA(1).getAttribute('href');return replace(el,feature(H[k],rev,h,k,fp(H[k])),fp(H[k]))}));
  upd('counters',fp(H.counters),el=>{show(el,!!H.counters.length);el.innerHTML=H.counters.map(c=>`<div class="stat reveal in"><b data-count="${esc(c.value)}" data-suffix="${esc(c.suffix)}">${esc(c.value)}${esc(c.suffix)}</b><span>${esc(c.label)}</span></div>`).join('')});
  upd('cta',fp([H.cta_image,H.cta_script,H.cta_title,H.cta_button]),el=>{txt(el.querySelector('.cta-in .script'),H.cta_script);heading(el.querySelector('h2'),H.cta_title);txt(el.querySelector('a.btn'),H.cta_button);return swapImg(el.querySelector('.cta-bg img'),H.cta_image)});
  upd('contact',fp([H.contact_eyebrow,H.contact_title,H.contact_text,H.contact_image]),el=>{txt(el.querySelector('.c-info .eyebrow'),H.contact_eyebrow);heading(el.querySelector('.c-info h2'),H.contact_title);txt(el.querySelector('.c-info>p'),H.contact_text);return swapImg(el.querySelector('.c-photo img'),H.contact_image)});
 }
 if(G){
  const gf=fp({photos:G.photos,yt:G.youtube,clips:G.videos}),gv=G.youtube.filter(v=>v.gallery);
  upd('gallery',gf,el=>{const used=new Set(G.photos.concat(gv).flatMap(g=>String(g.cats||'').split(/\s+/).filter(Boolean))),keys=['all'].concat(Object.keys(L.f).filter(k=>k!=='all'&&used.has(k)));
   const grid=el.querySelector('.g-grid'),bar=el.querySelector('.g-filters');show(el,!!(G.photos.length||gv.length));
   const items=tpl(G.photos.map(g=>`<button type="button" class="g-item reveal in" data-cat="${esc(g.cats)}" data-full="${esc(g.image)}" data-caption="${esc(g.alt)}"><img src="${esc(g.image)}" alt="${esc(g.alt)}" loading="lazy" decoding="async"${g.width?` width="${esc(g.width)}" height="${esc(g.height)}"`:''}><span>${esc(g.alt)}</span></button>`).join('')+gv.map(v=>`<div class="g-item g-vid reveal in" data-cat="${esc(v.cats)}">${yt(v)}</div>`).join(''));
   return sized(items).then(g=>{if(!g)return false;if(!keys.includes(curFilter))curFilter='all';
    bar.innerHTML=keys.map(k=>`<button type="button" data-filter="${k}"${k===curFilter?' class="on"':''} aria-pressed="${k===curFilter}">${esc(L.f[k])}</button>`).join('');
    grid.replaceChildren(items);if(curFilter!=='all')setFilter(curFilter);settle(el)})});
  upd('clips',gf,el=>{show(el,!!G.videos.length);const g=el.querySelector('.reel-grid');g.innerHTML=G.videos.map(c=>`<figure class="reel reveal in"><video muted loop playsinline preload="none" poster="${esc(c.poster)}" aria-label="${esc(c.title)}" data-reel><source src="${esc(c.video)}" type="video/mp4"></video><button type="button" class="reel-btn" aria-label="${esc(L.reel)}"></button><figcaption>${esc(c.title)}</figcaption></figure>`).join('');initReels(g)});
  upd('watch',gf,el=>{const f=G.youtube.find(v=>v.featured),sh=G.youtube.filter(v=>v.home&&!v.featured).slice(0,4);show(el,!!(f||sh.length));
   const top=el.querySelector('.w-top'),m=top.querySelector('.w-main');let n=null;
   if(f){n=document.createElement('div');n.className='w-main reveal in';n.innerHTML=yt(f)}
   if(m&&n)m.replaceWith(n);else if(m)m.remove();else if(n)top.prepend(n);
   let s=el.querySelector('.w-shorts');
   if(sh.length){const w=document.createElement('div');w.className='w-shorts';w.innerHTML=sh.map(v=>`<div class="reveal in">${yt(v)}</div>`).join('');if(s)s.replaceWith(w);else el.append(w)}else if(s)s.remove();
   return sized(el).then(g=>{settle(el);return g})});
 }
 if(SV&&S)upd('services',fp(SV.results),el=>{const html=SV.results.map((s,i)=>{const n=i+1;return `<article class="svc wrap ${n%2?'':'svc-rev'}" id="service-${esc(s.id)}"><div class="f-img reveal-img in"><img src="${esc(s.image)}" alt="${esc(s.title)}" loading="lazy" decoding="async" data-tilt><span class="num">${String(n).padStart(2,'0')}</span></div><div class="f-text"><span class="eyebrow reveal in">${esc(s.eyebrow)}</span><h2 class="split in">${esc(s.title)}</h2><p class="reveal in">${s.description.map(esc).join('<br>')}</p><div class="reveal in btnrow">${S.booking_url?bookA(L.bo,'',S.booking_url)+'<a class="link" href="'+esc(S.phone_href)+'" data-s="phone">'+esc(S.phone)+'</a>':'<a class="btn" href="'+esc(S.phone_href)+'" data-s="tel">'+esc(L.bk)+'</a>'}</div>${s.slug?'<p class="reveal in svc-more"><a class="link" href="'+esc(root+s.slug+(/\.html$/.test(b.dataset.post||'')?'.html':''))+'">'+esc(L.more)+' →</a></p>':''}${s.videos&&s.videos.length?'<div class="svc-vids reveal in">'+s.videos.map(yt).join('')+'</div>':''}</div></article>`}).join('');
  const t=tpl(html);return sized(t).then(g=>{if(!g)return false;el.replaceChildren(t);settle(el)})});
 if(SV&&svcId){const s=SV.results.find(x=>String(x.id)===svcId);   // service page (/carbon-peeling): lead, body, videos
  if(s)upd('svc',fp([s.description,s.blocks,s.videos]),el=>{const t=tpl(`<p class="sp-lead">${s.description.map(esc).join('<br>')}</p>`+s.blocks.map(k=>k.type==='h'?`<h2>${esc(k.text)}</h2>`:k.type==='ul'?`<ul>${k.items.map(i=>'<li>'+esc(i)+'</li>').join('')}</ul>`:`<p>${esc(k.text)}</p>`).join('')+(s.videos&&s.videos.length?`<h2>${esc(L.vids)}</h2><div class="svc-vids">${s.videos.map(yt).join('')}</div>`:''));
   return sized(t).then(g=>{if(!g)return false;el.replaceChildren(t);settle(el)})})}
 if(B){
  upd('blog',fp(nourl(B.results)),el=>{const html=B.results.length?`<div class="bgrid" data-live="blog">${B.results.map(card).join('')}</div>`:`<p class="b-empty" data-live="blog">${esc(L.empty)}</p>`;return replace(el,html,fp(nourl(B.results)))});
  if(slug){const rest=B.results.filter(p=>p.slug!==slug).slice(0,2),sec=document.querySelector('[data-live=more]');
   if(sec)upd('more',fp(nourl(rest)),el=>{show(el,!!rest.length);const g=el.querySelector('.bgrid'),t=tpl(rest.map(card).join(''));return sized(t).then(k=>{if(!k)return false;g.replaceChildren(t);settle(el)})});
   if(D.post&&D.post.s===404&&!B.results.some(p=>p.slug===slug)){const a=document.querySelector('.post-back');if(a)location.replace(a.href)}}
 }
 if(P&&P.slug===slug)upd('post',fp(nourl(P)),el=>{const sh=document.querySelector('.subhero');
  txt(sh.querySelector('.script'),P.date);heading(sh.querySelector('h1'),P.title);const old=document.title.split(' | ')[0];if(old!==P.title)document.title=document.title.replace(old,P.title);
  const t=tpl(faqMark(P.blocks).map(k=>k.type==='q'?`<h3 class="faq-q">${esc(k.text)}</h3>`:k.type==='h'?`<h2>${esc(k.text)}</h2>`:k.type==='ul'?`<ul>${k.items.map(i=>'<li>'+linkify(i)+'</li>').join('')}</ul>`:`<p>${linkify(k.text)}</p>`).join('')+(P.videos||[]).map(v=>`<figure class="post-vid">${yt(v)}</figure>`).join(''));
  return Promise.all([swapImg(sh.querySelector('.subhero-bg img'),P.cover),sized(t)]).then(r=>{if(!r.every(Boolean))return false;el.replaceChildren(t);settle(el)})});
};

const run=()=>{const w=[J('settings','/api/settings/')];
 if(document.querySelector('.hero'))w.push(J('home','/api/home/'));
 if(document.querySelector('[data-live=gallery],[data-live=clips],[data-live=watch]'))w.push(J('gallery','/api/gallery/'));
 if(document.querySelector('[data-live=services],[data-live=svc]'))w.push(J('services','/api/services/'));
 if(document.querySelector('[data-live=blog],[data-live=more]')||slug)w.push(J('blog','/api/blog/'));
 if(slug)w.push(J('post','/api/blog/'+encodeURIComponent(slug)+'/'));
 render();   // cached data (stale) first, then every fresh response
 w.forEach(p=>p.then(render))};
const start=()=>setTimeout(run,300);
document.readyState==='complete'?start():addEventListener('load',start)}}
})();
// ---- first-visit discount popup: e-mail -> POST {api}/api/discount-signup/ (shown once; 7 days pause after closing; never after signup) ----
(()=>{const b=document.body,api=(b.dataset.api||'').replace(/\/api\/contact\/?$/,'').replace(/\/+$/,'');if(!/^https?:|^\//.test(api)||!window.fetch)return;
const K='ic-popup',now=Date.now();let st;try{st=JSON.parse(localStorage.getItem(K)||'null')}catch(e){return}
if(st&&(st.done||now-st.t<7*864e5))return;
const hu=b.dataset.lang==='hu',save=o=>{try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}};
const T=hu?{t:'{p}% kedvezmény az első kezelésből',x:'Add meg az e-mail címed, és az első látogatásodkor {p}% kedvezményt adunk.',em:'E-mail cím',ph:'nev@pelda.hu',c:'Hozzájárulok, hogy az Infinite Care e-mailben elküldje az ajánlatot és marketing leveleket küldjön. A hozzájárulás bármikor visszavonható.',go:'Kérem a kedvezményt',cl:'Bezárás',ok:'Köszönjük! Az első látogatásodkor {p}% kedvezményt kapsz – foglaláskor vagy a látogatáskor említsd meg ezt az e-mail címet.',code:'Kuponkód: ',bk:'Időpontfoglalás online',dup:'Ez az e-mail cím már regisztrálva van.',inv:'Kérjük, adj meg érvényes e-mail címet, és fogadd el a hozzájárulást.',net:'Hálózati hiba – kérjük, próbáld újra.',rl:'Túl sok próbálkozás – kérjük, próbáld újra később.'}
 :{t:'{p}% off your first visit',x:'Enter your e-mail and get {p}% off your first treatment at Infinite Care.',em:'E-mail address',ph:'name@example.com',c:'I agree to receive the offer and marketing e-mails from Infinite Care. I can withdraw my consent at any time.',go:'Get my discount',cl:'Close',ok:'Thank you! You get {p}% off your first visit – just mention this e-mail address when you book or at your visit.',code:'Coupon code: ',bk:'Book online',dup:'This e-mail address is already registered.',inv:'Please enter a valid e-mail address and tick the consent box.',net:'Network error – please try again.',rl:'Too many attempts – please try again later.'};
let shown=false;const open=s=>{if(shown)return;shown=true;const P=s.percent||10,f=v=>v.replace(/\{p\}/g,P),bk=s.booking_url||'https://l.fresha.com/3dvz3n7j6';
 const last=document.activeElement,d=document.createElement('div');d.className='dp-wrap';
 d.innerHTML=`<div class="dp" role="dialog" aria-modal="true" aria-labelledby="dp-t" aria-describedby="dp-x"><button type="button" class="dp-x" aria-label="${T.cl}">×</button><p class="dp-pc" aria-hidden="true">−${P}%</p><h2 id="dp-t"></h2><p id="dp-x"></p><form novalidate><label for="dp-e">${T.em}</label><input id="dp-e" name="email" type="email" required autocomplete="email" inputmode="email" placeholder="${T.ph}"><input class="dp-hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"><label class="dp-c"><input type="checkbox" name="consent" required> <span>${T.c}</span></label><button class="btn" type="submit">${T.go}</button><p class="dp-m" role="status" aria-live="polite"></p></form></div>`;
 d.querySelector('h2').textContent=s.title||f(T.t);d.querySelector('#dp-x').textContent=s.text||f(T.x);
 const dlg=d.querySelector('.dp'),fm=d.querySelector('form'),m=d.querySelector('.dp-m'),btn=fm.querySelector('[type=submit]');
 const close=()=>{d.remove();removeEventListener('keydown',key,true);const x=JSON.parse(localStorage.getItem(K)||'{}');if(!x.done)save({t:Date.now()});if(last&&last.focus)last.focus()};
 const key=e=>{if(e.key==='Escape'){e.preventDefault();close()}else if(e.key==='Tab'){const fs=[...dlg.querySelectorAll('button,input:not(.dp-hp),a[href]')].filter(x=>x.offsetParent),a=fs[0],z=fs[fs.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}};
 d.addEventListener('click',e=>{if(e.target===d||e.target.closest('.dp-x'))close()});addEventListener('keydown',key,true);
 const msg=(t,c)=>{m.textContent=t;m.className='dp-m '+c};
 fm.addEventListener('submit',async e=>{e.preventDefault();const em=fm.email.value.trim();if(!fm.email.checkValidity()||!em||!fm.consent.checked){msg(T.inv,'err');return}
  btn.disabled=true;msg('','');let r;try{const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),12000);r=await fetch(api+'/api/discount-signup/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:em,consent:true,lang:hu?'hu':'en',page:location.pathname,website:fm.website.value}),signal:ctl.signal});clearTimeout(to)}catch(x){btn.disabled=false;msg(T.net,'err');return}
  btn.disabled=false;
  if(r.status===201){save({done:1,t:Date.now()});const o=document.createElement('div');o.className='dp-ok';const p=document.createElement('p');p.textContent=f(T.ok);o.append(p);if(s.code){const c=document.createElement('p');c.className='dp-code';c.textContent=T.code+s.code;o.append(c)}const a=document.createElement('a');a.className='btn';a.href=bk;a.target='_blank';a.rel='noopener noreferrer';a.textContent=T.bk;o.append(a);fm.replaceWith(o);a.focus()}
  else msg(r.status===409?T.dup:r.status===422?T.inv:r.status===429?T.rl:T.net,'err')});
 b.append(d);requestAnimationFrame(()=>d.classList.add('on'));fm.email.focus({preventScroll:true})};
const go=()=>{removeEventListener('scroll',go);clearTimeout(tm);const u=api+'/api/settings/?lang='+(hu?'hu':'en');let c;try{c=JSON.parse(sessionStorage.getItem('ic:'+u)||'null')}catch(e){}
 const use=s=>{if(s&&s.popup&&s.popup.enabled===false)return;open({...(s&&s.popup||{}),booking_url:s&&s.booking_url})};
 if(c&&c.d)use(c.d);else fetch(u,{headers:{Accept:'application/json'}}).then(r=>r.ok?r.json():null).then(use,()=>use(null))};
let tm;const arm=()=>{tm=setTimeout(go,4000);addEventListener('scroll',go,{passive:true,once:true})};
document.readyState==='complete'?arm():addEventListener('load',arm)})();
