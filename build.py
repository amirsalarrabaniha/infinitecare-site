# Generates the static HTML pages (shared header/footer). Run: python3 build.py
I='assets/images/'
def head(title,active):
    nav=''.join(f'<a href="{h}" class="{"active" if k==active else ""}">{t}</a>' for k,h,t in [('home','index.html','Home'),('services','services.html','Our treatments'),('prices','prices.html','Our prices'),('offers','services.html#packages','Offers')])
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | Infinite Care Beauty Clinic</title><meta name="description" content="Infinite Care Beauty Clinic – The Beauty of Health. Budapest, Podmaniczky str. 5.">
<link rel="icon" href="{I}favicon.ico"><link rel="icon" sizes="96x96" href="{I}infinitecare-96.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500&family=Mr+Dafoe&family=Playfair+Display:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="css/style.css"></head><body class="page-{active}">
<div class="loader"><img src="{I}infinitecare-logo-4.png" alt=""></div><div class="cursor-glow"></div><div class="progress"></div>
<header class="nav"><a href="index.html" class="brand"><img class="logo-light" src="{I}infinitecare-logo-2.png" alt="Infinite Care"><img class="logo-dark" src="{I}infinitecare-logo-1.png" alt="Infinite Care"></a>
<nav class="menu">{nav}<a class="lang" href="https://www.infinitecare.hu/fooldal">HU</a></nav>
<a class="btn btn-sm nav-cta" href="tel:+3617070075">+36 1 707 0075</a><button class="burger" aria-label="Menu"><span></span><span></span></button></header>
'''
def subhero(title,img):
    return f'''<section class="subhero"><div class="subhero-bg" data-parallax style="background-image:url({I}{img})"></div><div class="subhero-in">
<span class="script reveal">Beauty Clinic</span><h1 class="split">{title}</h1><a class="btn reveal" href="tel:+3617070075">+36 1 707 0075</a></div></section>'''
FOOT=f'''<footer class="footer"><div class="wrap fgrid">
<div class="reveal"><img src="{I}infinitecare-logo-2.png" alt="Infinite Care" class="flogo"><p class="script">Beauty Clinic</p></div>
<div class="reveal"><h4>Open hours:</h4><p>Mon-Fri: 9 - 20<br>Sat: 9 - 15</p></div>
<div class="reveal"><h4>Reservation:</h4><p><a href="tel:+3617070075">+36 1 707 0075</a><br>Bp. VI. Podmaniczky str. 5.<br><a href="mailto:info@infinitecare.hu">info@infinitecare.hu</a></p></div>
<div class="reveal social"><a href="https://www.facebook.com/profile.php?id=100092186686742" aria-label="Facebook">f</a><a href="https://www.instagram.com/infinitecarebeauty" aria-label="Instagram">ig</a><a href="https://youtube.com/@InfiniteCareBeautyClinic" aria-label="YouTube">yt</a></div>
</div><div class="wrap fbottom"><span>Budapest, Hungary</span><span>Infinite Care - The Beauty of Health</span></div></footer>
<script src="js/main.js"></script></body></html>'''

home=head('Home','home')+f'''
<section class="hero"><div class="hero-bg" data-parallax style="background-image:url({I}main-banner.jpg)"></div><div class="hero-veil"></div>
<div class="hero-in"><img class="hero-logo" src="{I}infinitecare-logo-4.png" alt="">
<span class="script hero-script">Hello Beautiful!</span>
<h1 class="split">Infinite Care<br><em>health and beauty</em></h1>
<p class="lead reveal">Welcome to the Infinite Care Beauty Clinic! Our highly educated and experienced beauty team are waiting for you in the heart of Budapest. Let's find together the harmony between body and soul. Infinite Care health and beauty.</p>
<div class="hero-btns reveal"><a class="btn" href="services.html">Our treatments</a><a class="btn btn-ghost" href="#contact">Contact</a></div></div>
<div class="scroll-hint"><span></span></div></section>

<section class="marquee"><div class="marquee-track">{"".join(f"<span>{w}</span><i>✦</i>" for w in ["Exosome Therapy","Laser hair removal","Mesotherapy","Emsculpt","Carbon peeling","Teeth whitening","Face lifting","Brazilift","Massage"]*2)}</div></section>

<section class="feature wrap"><div class="f-img reveal-img"><img src="{I}box-1.jpg" alt="Enhance your beauty" data-tilt></div>
<div class="f-text"><span class="eyebrow reveal">Our treatments</span><h2 class="split">Enhance your beauty</h2>
<p class="reveal">Let your face, skin and your whole body smile to the world! Let's shine brighter! You deserve to be beautiful in every single minute of your life.</p>
<p class="reveal">Our highly educated beauty team, brand new treatments and techniques and the most powerful machines are waiting for you in our clinic!</p>
<a class="btn reveal" href="services.html">Our treatments</a></div></section>

<section class="stats wrap">{"".join(f'<div class="stat reveal"><b data-count="{n}">0</b><span>{t}</span></div>' for n,t in [(11,"treatments"),(4,"packages"),(6,"days a week"),(70,"price items")])}</section>

<section class="feature feature-rev wrap"><div class="f-img reveal-img"><img src="{I}box-2.jpg" alt="Perfect harmony" data-tilt></div>
<div class="f-text"><span class="eyebrow reveal">Perfect harmony</span><h2 class="split">The beautiful body is waiting for you!</h2>
<p class="reveal">When did you feel last time that your body and soul were in harmony? When you felt that everything is perfect and you don't need anything just to enjoy the moment you are living in?</p>
<p class="reveal">We help you to find the harmony between your body and soul!</p>
<a class="btn reveal" href="prices.html">Learn more about us!</a></div></section>

<section class="cta"><div class="cta-bg" data-parallax style="background-image:url({I}services.jpg)"></div><div class="cta-in">
<span class="script reveal">Beauty and health</span><h2 class="split">We are waiting for you to a consultation</h2><a class="btn reveal" href="tel:+3617070075">+36 1 707 0075</a></div></section>

<section class="contact wrap" id="contact"><div class="c-info"><span class="eyebrow reveal">Contact</span><h2 class="split">Beauty and health</h2>
<p class="reveal">Have you got any questions about us or our treatments? keep in touch we get back to you!</p>
<form class="cform reveal" onsubmit="event.preventDefault();location.href='mailto:info@infinitecare.hu?subject=Infinite%20Care&body='+encodeURIComponent(this.msg.value+'\\n\\n'+this.name.value+' '+this.email.value)">
<label><input name="name" required placeholder=" "><span>Name</span></label><label><input name="email" type="email" required placeholder=" "><span>E-mail</span></label>
<label><textarea name="msg" rows="4" required placeholder=" "></textarea><span>Message</span></label><button class="btn">Send</button></form></div>
<div class="map reveal-img"><iframe loading="lazy" title="Map" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2695.108056800498!2d19.053390076740023!3d47.50728679483003!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x4741dd16d7887141%3A0x615a4db6ad2f2ed2!2sInfinite%20Care%20Beauty%20Clinic!5e0!3m2!1sen!2sen!4v1689769315232!5m2!1sen!2sen"></iframe></div></section>
'''+FOOT

S=[("box-14","Brand new, Worldwide innovation","Exosome Therapy","Exosome therapy offers several benefits as a standalone treatment, including reduced inflammation, improved tissue repair, and enhanced collagen production. This makes exosomes particularly effective in reducing the appearance of wrinkles, uneven skin tone, pigmentation, promoting wound healing, hair and scalp problems and treating scars."),
("box-2","Soft and infinitely smooth","Laser hair removal","Smooth and hairless body all over the year? Yes, it's possible! We all know the feeling when our body is not perfectly shaved and hairless. We have the best solution for this problem! Painless and permanent hair removal. Visible result after the first treatment. Ideal solution for men as well!"),
("box-12","Bio-rejuvenation for the flawless skin","Mesotherapy with micro needles","Recent days perfectly clean and even skin tone are a must have. Here in Infinite Care Beauty Clinic we help you to achieve your perfect skin goal with our pure Revitalize serums used for micro needling Mesotherapy."),
("box-3","Perfect body all over the year","Emsculpt treatment","Perfect body within two weeks with electric muscle stimulation! The EMSCULPT is the best solution if you want to build muscles and burn fat at the same time!"),
("box-4","Good bye cellulite","Cellulite therapy","Anti cellulite treatment for flawlessly perfect body with ultrasound technology what burns fat and tighten the skin on the critical areas."),
None,
("box-5","Experience the flawless and radiant skin","Carbon peeling","The anti-aging carbon peeling gives everything what your skin needs. Ideal for scares and wrinkles, lightens the dark and uneven spots on your skin for a more beautiful skin tone. We recommend this treatment all over the body."),
("box-6","The secret of the perfect smile","Teeth whitening","Hollywood smile without pain in 30 or 60 minutes. It's a must have treatment you will ever need for the whiter and brighter looking teeth."),
("box-7","Happy life without wrinkles","Face lifting","Our face is the most important part of our body. We have to take care of it as much as possible and give everything it needs. Our ultimate machines are the best options to spoil the skin on your face."),
("box-8","Plumped lips, wrinkle free skin","Esthetic treatments","Wrinkle free face, beautiful and plumped lips, tighter skin, excellent nose. You can find everything in our beauty clinic what you need: Botox, Lip fillers, Russian lips technique, filler for cheeks, chin and jaw line, nose correction, face slimming, double chin removal, collagen therapy, skin booster, body fat dissolving, mesotherapy."),
("box-9","Bigger and tighter buttocks and boobs","Brazilift","If you don't like the shape of your buttocks or you want naturally plumped and bigger boobs you are in a right place! BRAZILIFT is the ultimate treatment for bigger and tighter buttocks and more plumped boobs. Try our painless Brazilian lift and your body will look like as a body of a Brazilian supermodel."),
("box-11","Pampering treatments, skin care","Massage","Choose from our massages:<br>Face massage, aromatherapy massage, deep relaxation massage, hydrating massage, energetic massage, cellulite Massage, honey massage, chocolate massage")]
P=[("Slim",["EMSCULPT 6 treatment","U Shaping Cellulite Therapy 6 treatments"],"309 000"),
("Bridal",["Laser hair removal - 6 treatments (full body)","EMSCULPT - 6 treatments","Carbon Peeling - 2 treatments","Teeth Whitening (60 minutes)"],"719 000"),
("Summer",["Laser hair removal - 6 treatments (full body)","EMSCULPT - 6 treatments","Cellulite treatment 6 treatments","Teeth Whitening (60 minutes)"],"799 000"),
("Business",["Laser Hair Removal - 6 treatments","EMSCULPT - 4 treatments","Cellulite therapy - 4 treatments","Teeth Whitening - 4 treatments"],"459 000")]
body=''; n=0
for s in S:
    if s is None:
        body+=f'''<section class="packages" id="packages"><div class="pk-bg" style="background-image:url({I}packages.png)"></div><div class="wrap"><span class="eyebrow light reveal">Offers</span><h2 class="split">Our most popular packages</h2><div class="pk-grid">'''
        body+=''.join(f'<div class="pk reveal" data-tilt><h3>{a}<span class="script">package</span></h3><ul>{"".join(f"<li>{x}</li>" for x in l)}</ul><b class="price">{p} <small>HUF</small></b><a class="btn" href="tel:+3617070075">Book an appointment</a></div>' for a,l,p in P)
        body+='</div></div></section>'; continue
    n+=1
    body+=f'''<article class="svc wrap {"svc-rev" if n%2==0 else ""}"><div class="f-img reveal-img"><img src="{I}{s[0]}.jpg" alt="{s[2]}" loading="lazy" data-tilt><span class="num">{n:02d}</span></div>
<div class="f-text"><span class="eyebrow reveal">{s[1]}</span><h2 class="split">{s[2]}</h2><p class="reveal">{s[3]}</p><div class="reveal btnrow"><a class="btn" href="tel:+3617070075">Book an appointment</a><a class="link" href="prices.html">Details →</a></div></div></article>'''
services=head('Our treatments','services')+subhero('Our treatments','services.jpg')+'<main class="svcs">'+body+'</main>'+FOOT

raw=open('data/prices.txt').read().strip().split('\n')
pr=''; cards=[]; cur=None
for line in raw:
    line=line.strip()
    if line.startswith('#'): cur=[line[1:].strip(),[]]; cards.append(cur)
    elif '|' in line: k,v=line.split('|'); cur[1].append(('row',k,v))
    else: cur[1].append(('sub',line,''))
for t,rows in cards:
    pr+=f'<div class="pcard reveal"><h3>{t}</h3>'+''.join((f'<div class="prow"><span>{k}</span><i></i><b>{v}</b></div>' if ty=='row' else f'<div class="psub">{k}</div>') for ty,k,v in rows)+'</div>'
prices=head('Our prices','prices')+subhero('Our prices','prices.jpg')+f'<main class="wrap prices">{pr}</main>'+FOOT
for f,c in [('index.html',home),('services.html',services),('prices.html',prices)]: open(f,'w').write(c)
