// Contact API URL. Pages rendered by Django set <body data-api="/api/contact/">.
// For the static GitHub Pages copy, set this to your deployed backend (e.g. 'https://infinitecare.onrender.com/api/contact/');
// when empty and no data-api is present the form falls back to a mailto: link.
const API_URL = '';
(()=>{const b=document.body,nav=document.querySelector('.nav'),prog=document.querySelector('.progress');
addEventListener('load',()=>setTimeout(()=>b.classList.add('loaded'),300));setTimeout(()=>b.classList.add('loaded'),2500);
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
const hero=document.querySelector('.hero h1');if(hero)setTimeout(()=>hero.classList.add('in'),1300);
function count(el){const t=+el.dataset.count,s=performance.now();const f=n=>{const p=Math.min((n-s)/1800,1);el.textContent=Math.round(t*(1-Math.pow(1-p,4)))+(p===1?(el.dataset.suffix??''):'');if(p<1)requestAnimationFrame(f)};requestAnimationFrame(f)}
// scroll: nav, progress, parallax
const px=[...document.querySelectorAll('[data-parallax]')];
const onS=()=>{const y=scrollY;nav.classList.toggle('scrolled',y>60);prog.style.width=y/(document.documentElement.scrollHeight-innerHeight)*100+'%';px.forEach(el=>{const r=el.parentElement.getBoundingClientRect();if(r.bottom>0&&r.top<innerHeight)el.style.transform=`translate3d(0,${(r.top)*-.18}px,0)`})};
addEventListener('scroll',onS,{passive:true});onS();
// tilt + cursor glow (pointer devices)
if(matchMedia('(hover:hover)').matches){const g=document.querySelector('.cursor-glow');addEventListener('mousemove',e=>{g.style.left=e.clientX+'px';g.style.top=e.clientY+'px'});
document.querySelectorAll('[data-tilt]').forEach(el=>{const t=el.closest('.f-img')||el;t.addEventListener('mousemove',e=>{const r=t.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;t.style.transform=`perspective(900px) rotateY(${x*6}deg) rotateX(${-y*6}deg)`});t.addEventListener('mouseleave',()=>t.style.transform='')})}

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
