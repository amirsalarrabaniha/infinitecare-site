"""Starting content of the service landing pages (/carbon-peeling, /carbon-hamlasztas, ...), taken from the previous
infinitecare.hu website so the URLs Google already knows keep working with the same keywords. Prices are not included.

`fill(Service)` only fills EMPTY fields of the existing services (matched by their English title), so edits made in the
admin are never overwritten. Used by migration 0009 and by `load_initial_content`.
"""

PAGES = [
    dict(match='exosome', slug_en='exosome-therapy', slug_hu='exoszoma-terapia', gallery_category='facial',
         meta_title_en='Exosome therapy in Budapest', meta_title_hu='Exoszóma terápia Budapesten',
         meta_description_en='Exosome therapy at Infinite Care Beauty Clinic, Budapest: reduced inflammation, improved tissue repair and enhanced collagen production for wrinkles, pigmentation, scars and scalp problems.',
         meta_description_hu='Exoszóma terápia az Infinite Care Beauty Clinicben, Budapest: sebgyógyító, antioxidáns és gyulladáscsökkentő hatás ráncokra, pigmentfoltokra, hegekre, haj- és fejbőrproblémákra.',
         body_en="""Brand new, worldwide innovation with exosome stem cells!

Exosome therapy offers several benefits as a standalone treatment, including reduced inflammation, improved tissue repair and enhanced collagen production. This makes exosomes particularly effective in reducing the appearance of wrinkles, uneven skin tone and pigmentation, promoting wound healing, treating hair and scalp problems and scars.

## Benefits

- Reduced inflammation
- Improved tissue repair
- Enhanced collagen production
- Fewer visible wrinkles, a more even skin tone and less pigmentation
- Support for hair and scalp problems and for scars

## What is exosome?

Exosomes are the natural by-product of cells. They are often described as microscopic bubbles or, in the scientific world, as nano extracellular vesicles. It is now recognised that these tiny molecules have an enormous role to play in skin and hair rejuvenation.

## How often do I need exosome therapy?

We suggest a treatment every second week, 3-4 times, depending on your skin's condition. In certain cases we may offer you a weekly treatment. Before starting the exosome therapy we hold a consultation free of charge.""",
         body_hu="""Világújdonság a szépségápolásban az exoszómák őssejtjeinek erejével!

Az exoszómák a szépségiparban új és ígéretes területet jelentenek. A növényi exoszómák különböző biológiai és farmakológiai hatásokat fejtenek ki, mint például sebgyógyítás, antioxidáns és gyulladáscsökkentő hatások, pigmentkezelés, haj- és fejbőrproblémák kezelése.

## Előnyei

- Sebgyógyító hatás
- Antioxidáns és gyulladáscsökkentő hatás
- Pigmentfoltok kezelése
- Haj- és fejbőrproblémák kezelése

## Mi az az exoszóma?

Az exoszómás komplexum egy olyan biológiai rendszer, amely sejtekben található, és olyan apró vezikulumokat, azaz membránnal borított kis "hólyagokat" tartalmaz, amelyek információt vagy más anyagokat hordoznak más sejtekhez. Ezek a komplexek különféle feladatokat látnak el, mint például az üzenetek továbbítása, az immunrendszer működésének szabályozása vagy a sejtek környezetével való kommunikáció.

## Milyen gyakran kell exoszóma kezelésre járnom?

A bőr állapotától függően általában kéthetente ajánljuk az exoszóma terápiát 3-4 alkalommal, de egyes esetekben szükség lehet heti egy kezelésre. Ezt minden esetben egy előzetes, ingyenes konzultáción beszéljük meg pácienseinkkel."""),

    dict(match='laser hair', slug_en='laser-hair-removal', slug_hu='lezeres-tartos-szortelenites', gallery_category='laser',
         meta_title_en='Laser hair removal in Budapest – painless, permanent',
         meta_title_hu='Lézeres tartós szőrtelenítés Budapesten',
         meta_description_en='Painless, permanent laser hair removal with our brand new laser machine in Budapest. Visible results after the first few treatments. Before and after care tips.',
         meta_description_hu='Fájdalommentes, gyors lézeres tartós szőrtelenítés a legújabb dióda lézerrel Budapesten. 6-12 alkalom a tartós eredményért. Tudnivalók a kezelés előtt és után.',
         body_en="""Painless, permanent hair removal with our brand new laser machine. Visible results after the first few treatments.

## How it works

Depending on your skin and hair type we recommend a minimum of 6-12 treatments. Come every 4 weeks for the best result.

## Before laser hair removal

- Shave the area with a razor one day before the treatment.
- Don't use wax or an epilator!
- Wash your skin carefully before the treatment and don't leave any perfume or body lotion on it.

## After laser hair removal

- Avoid direct sunlight and hot baths for 1-2 days.
- Use sun protection!
- In case of irritation use aloe vera gel.

## Between treatments

Shave regularly with a razor; don't use wax or an epilator.""",
         body_hu="""Fájdalommentes, gyors eljárás, melyet a legújabb dióda lézeres kezelőegységünkkel végzünk.

## Hogyan működik?

Téli időszakban érdemes elkezdeni, 4 hetente ismételve. Bőr- és szőrtípustól függően minimum 6-12 alkalmat javasolunk a tartós és végleges eredmény eléréséhez.

## Kezelés előtt

- Borotvával szőrtelenítsük a kezelendő felületet egy nappal a lézeres szőrtelenítés előtt.
- A kezelés napján ne legyen a szőrtelenítendő bőrfelületen sem dezodor, sem testápoló.

## Kezelés után

- Kerüljük a közvetlen napsugárzást és a forró kádfürdőt 1-2 napig!
- Használjunk magas faktorszámú naptejet!

## Két kezelés között

Csak borotvával szőrtelenítsünk, ne használjunk sem epilátort, sem gyantát."""),

    dict(match='meso', slug_en='mesotherapy', slug_hu='mezoterapia', gallery_category='facial',
         meta_title_en='Mesotherapy with Revitalize serums in Budapest',
         meta_title_hu='Mezoterápia Revitalize szérumokkal Budapesten',
         meta_description_en='Mesotherapy is a non-surgical technique that delivers vitamins, plant extracts and other ingredients into the skin with micro needles. Revitalize serums for skin, body and hair in Budapest.',
         meta_description_hu='A mezoterápia műtét nélküli technika: vitaminokat, növényi kivonatokat és egyéb összetevőket juttat mikrotűkkel a bőrbe. Revitalize szérumok bőrre, testre és hajra Budapesten.',
         body_en="""## What is mesotherapy?

Mesotherapy is a non-surgical technique that uses micro-injections of pharmaceutical or homeopathic preparations, plant extracts, vitamins and other ingredients into the skin and subcutaneous fat. There are many published studies on the clinical treatments and effects of these preparations.

## How long will it last?

Mesotherapy is usually given in a course of treatment with results lasting between 3-5 months. Top-up treatments are required to maintain the results, and treatment protocols vary depending on the indication and the serum used.

## Who is it for?

It is ideal for those who are in generally good health but are troubled by the appearance of wrinkles, uneven skin texture, sagging skin or cellulite, or who want to kick-start a visible complexion transformation.

## What can you expect after a Revitalize treatment?

- Skin rejuvenation: a glowing complexion, more hydrated skin with less visible wrinkles
- Skin tightening: improved skin tone and greater elasticity as collagen and elastin fibres build within the skin
- Cellulite: fat cells are dissolved, improving the appearance of cellulite; stubborn fat pockets shrink
- Hair rejuvenation: a healthier scalp, stronger existing hair, and dormant hair follicles stimulated to create new hair growth
- Acne and scarring: scars become smoother and less visible, acne and blemishes resolve for a clearer complexion

## The secret of Revitalize

MyFiller Revitalize has been developed by a team of experts dedicated to bringing "new life to the skin". The range of serums expands to accommodate the demands of today's clients.

## Serums you can choose from

- Revitalize Pure – uneven skin tone and hydration: collagen balanced with hyaluronic acid for stretch marks, acne marks, scars and other skin imperfections
- Revitalize Essence – smoothing wrinkles and skin imperfections: high and low density hyaluronic acid for optimum hydration
- Revitalize Vitamins – nourishment from the inside out: hyaluronic acid, vitamins, amino acids, minerals and coenzymes for revitalized, radiant skin
- Revitalize Body – firming and shaping: for flaccidity, stretch marks, after laser or peeling treatments
- Revitalize Slim – targeted fat dissolving: for localized fat on the belly, the back of the arms, the neck and the legs
- Revitalize White Skin – uneven skin tone and pigmentation: lightens the skin tone and reduces spots
- Revitalize Hair – stronger, healthier hair: nourishes the scalp and promotes hair growth""",
         body_hu="""A mezoterápia egy műtét nélküli technika, amely gyógyszerészeti vagy homeopátiás készítményeket, növényi kivonatokat, vitaminokat és egyéb összetevőket juttat mikrotűk segítségével a bőrbe és a bőr alatti zsírrétegbe. Számos publikált tanulmány található ezen készítmények klinikai kezeléséről és hatásairól.

## Tartóssága

A mezoterápiás kezelés általában 3-5 hónapos kúrákban ajánlott, az eredmények megőrzéséhez kiegészítő kezelések szükségesek, a kezelési protokollok pedig az indikációtól és a használt szérumtól függően változnak.

## Kinek ajánljuk?

Ideális azoknak, akik általában jó egészségnek örvendenek, de zavarja őket a ráncok megjelenése, az egyenetlen bőrszerkezet, a megereszkedett bőr vagy a narancsbőr, illetve azoknak, akik szeretnék láthatóan javítani az arcbőrük tónusát.

## Mire számíthatsz a Revitalize mezoterápiás kezelés után?

- Bőrfiatalítás: ragyogó arcszín, hidratáltabb bőr, kevésbé látható ráncok
- Bőrfeszesítés: a bőr tónusa javul, rugalmasabbá válik, ahogy a kollagén és elasztin rostok beépülnek a bőr szerkezetébe
- Cellulit: a zsírsejtek feloldódnak, javul a narancsbőr megjelenése, a makacs zsírpárnák összezsugorodnak
- Hajfiatalítás: egészségesebb fejbőr, erősebb haj, az alvó hajhagymák serkentése az új haj növekedéséért
- Akne és hegesedés: a hegek simábbá és kevésbé láthatóvá válnak, a pattanások és foltok megszűnnek

## A Revitalize titka

A MyFiller Revitalize-t egy szakértői csapat fejlesztette ki, amelynek célja, hogy "új életet vigyen a bőrbe". Ez lett a mi mottónk is!

## Választható szérumok

- Essence – azonnali és hosszan tartó eredmények: a nagy és kis molekulasúlyú hialuronsav egyensúlya hidratál és simítja a ráncokat
- Pure – a bőrhibák és az erőteljes hidratálás szakértője: kollagén és hialuronsav striákra, aknés hegekre, bőregyenetlenségekre
- Vitamins – belülről táplálja a bőrt: revitalizál és ragyogást biztosít
- Body – feszesíti a megereszkedett bőrt: petyhüdtség, striák, lézer és peeling utáni helyreállítás
- Slim – célzott zsírbontás: zsírfelhalmozódás a hason, a felkar hátsó részén, a nyakon és a lábakon
- White skin – halványítja a hiperpigmentált foltokat: bőrtónus világosítása és foltok halványítása
- Hair – erősíti a hajmátrixot: táplálja a fejbőrt, elősegíti a haj, a szakáll és a szemöldök növekedését"""),

    dict(match='emsculpt', slug_en='ems-treatment', slug_hu='ems-testkezeles', gallery_category='emsculpt',
         meta_title_en='EMSCULPT EMS body treatment in Budapest',
         meta_title_hu='EMSCULPT EMS testkezelés Budapesten',
         meta_description_en='EMSCULPT treatment: build muscle and burn fat with electric muscle stimulation (EMS). Faster results than conventional training, with no load on your joints. Budapest.',
         meta_description_hu='EMSCULPT testkezelés: az EMS, azaz elektromos izomstimuláció hatékony alakformáló edzésforma. Egy 20 perces kezelés kb. 60-90 perc edzéssel egyenértékű. Budapest.',
         body_en="""Perfect body with electric muscle stimulation (EMS).

## Benefits

- Faster effects than with any conventional training, thanks to the powerful muscle activation and the high number of muscles activated in each session
- Studies show that electrostimulation can activate up to 95% of the fibres of a muscle, compared to 60-70% in conventional training
- No additional loads, so there is no risk of injuring yourself
- No weights, so your joints do not suffer: there is no joint impact that overloads and wears out the joints

## How it works

Electrical impulses stimulate your muscles deeply and intensively. It is the best solution if you want to build muscle and burn fat at the same time.""",
         body_hu="""Az EMS, azaz elektromos izomstimuláció egy nagyon hatékony alakformáló edzésforma, melyben elektromos impulzusok segítségével stimuláljuk az izmokat.

## Előnyei

- Egy 20 perces kezelés megegyezik egy kb. 60-90 perces konditermi edzéssel, mivel az EMS az izmokat mélyen és intenzíven stimulálja
- Tökéletes időhiányban szenvedő vendégeink számára, akik gyors és hatékony eredményeket szeretnének elérni az alakformálás területén
- Nincs plusz terhelés, így az ízületeket sem terheli

## Hogyan működik?

Elektromos impulzusok stimulálják mélyen és intenzíven az izmokat. Izomépítés és zsírégetés egyszerre."""),

    dict(match='cellulite', slug_en='cellulite-therapy', slug_hu='cellulit-terapia', gallery_category='cellulite',
         meta_title_en='Cellulite therapy – U Shaping in Budapest',
         meta_title_hu='Cellulit (narancsbőr) terápia Budapesten',
         meta_description_en='Anti-cellulite treatment for a flawless body with radio frequency, infrared and vacuum (U Shaping) for smoother, tighter skin. Budapest.',
         meta_description_hu='Cellulit terápia rádiófrekvenciás, infravörös és vákuumos kezeléssel: segíti a zsírsejtek lebontását, feszesebb bőr, jobb vérkeringés. Infinite Care, Budapest.',
         body_en="""Anti-cellulite treatment for a flawlessly perfect body.

## How it works

The U Shaping treatment combines radio frequency, infrared and vacuum.

## Benefits

- Smoother skin with less visible cellulite
- Tighter skin on the critical areas
- Improved circulation""",
         body_hu="""A cellulit terápiánál egy rádiófrekvenciás, infravörös és vákuumos kezelés kombinációját használjuk.

## Hogyan működik?

A kezelés segíti a zsírsejtek feltörését, majd a nyirokáramba juttatását.

## Előnyei

- Rövid időn belül a narancsbőr eltűnik
- A bőr feszesebb lesz
- A vérkeringés helyreáll"""),

    dict(match='carbon', slug_en='carbon-peeling', slug_hu='carbon-hamlasztas', gallery_category='carbon',
         meta_title_en='Carbon peeling with laser in Budapest',
         meta_title_hu='Carbon hámlasztás – lézeres mélyhámlasztás Budapesten',
         meta_description_en='Anti-aging carbon peeling with laser for a perfectly tight and wrinkle free face. Ideal for scars and oily, uneven skin. Infinite Care Beauty Clinic, Budapest.',
         meta_description_hu='Speciális lézeres mélyhámlasztás, mely teljesen fájdalommentes és gyors eljárás: feszesebb, tisztább bőr, egységesebb bőrtónus, halványuló pigmentfoltok. Budapest.',
         body_en="""Anti-aging carbon peeling with laser for a perfectly tight and wrinkle free face. Ideal for scars and oily, uneven skin.

## Benefits

- Tighter, cleaner skin
- Fewer fine wrinkles
- Ideal for scars and for oily, uneven skin
- Lightens dark and uneven spots for a more even skin tone

## How does the treatment work?

Our beauty therapist cleans your face properly, then applies a special carbon mask mixed with minerals and vitamins. Once the mask has dried, we pop it off with our laser machine. Your eyes are covered with cotton pads and special laser glasses to protect them from the laser light. After the treatment we cleanse and hydrate your skin.""",
         body_hu="""Speciális lézeres mélyhámlasztás, mely teljesen fájdalommentes és gyors eljárás.

## Hogyan zajlik a kezelés?

A vendég egy szénnel és ásványi anyagokkal teli, fekete színű maszkot kap, melyet száradás után lézerrel "lepattogtatunk" az arcról.

## Előnyei

- A bőr feszesebb, tisztább, tónusosabb lesz
- Az apróbb ráncok eltűnnek
- A zsíros területek kitisztulnak, javul a bőrminőség
- A bőrtónus egységesebbé válik, halványulnak a pigmentfoltok"""),

    dict(match='teeth', slug_en='teeth-whitening', slug_hu='fogfeherites', gallery_category='whitening',
         meta_title_en='Laser teeth whitening in Budapest – Hollywood smile',
         meta_title_hu='Lézeres fogfehérítés Budapesten – hollywoodi mosoly',
         meta_description_en='Hollywood smile without pain in 60 minutes with our latest laser teeth whitening machine. How the treatment works. Infinite Care Beauty Clinic, Budapest.',
         meta_description_hu='Speciális, fájdalommentes, gyors és rendkívül látványos lézeres fogfehérítő eljárás, mely 60 perc alatt igazi hollywoodi mosolyt varázsol. Budapest.',
         body_en="""Hollywood smile without pain in 60 minutes with our latest laser machine!

## How does the treatment work?

- Before the treatment we ask you to brush your teeth properly. Don't worry, we give you a toothbrush and toothpaste.
- We apply a special gum protector and put the whitening serum on your teeth.
- We place the laser machine close to your mouth.
- Now you only need to relax for 60 minutes, then enjoy your perfectly white Hollywood smile!""",
         body_hu="""Speciális, fájdalommentes, gyors és rendkívül látványos lézeres fogfehérítő eljárás, mely 60 perc alatt igazi hollywoodi mosolyt varázsol.

## Hogyan zajlik a kezelés?

- Kezelés előtt megkérjük kedves vendégünket, hogy alaposan mosson fogat az általunk biztosított fogkrémmel és fogkefével.
- Feltesszük a fogínyvédő zselét, majd felkenjük a speciális fogfehérítő szérumunkat.
- Beállítjuk a lézert, amit a fogak közelébe helyezünk.
- Ezek után nincs más dolgod, csak relaxálni 60 percig, majd élvezni a hófehér hollywoodi mosolyt!"""),

    dict(match='face lifting', slug_en='face-lifting-en', slug_hu='face-lifting', gallery_category='facial',
         meta_title_en='Facelifting (RF) – non-surgical face lift in Budapest',
         meta_title_hu='Facelifting – gépi arcfeszesítés Budapesten',
         meta_description_en='Non-surgical facelifting: radio frequency skin tightening with infrared and vacuum stimulates collagen, elastin and new skin cells to firm and lift sagging skin. Budapest.',
         meta_description_hu='Kellemes, pihentető arckezelés, mely egyesíti a rádiófrekvencia, az infravörös fény és a vákuum jótékony hatásait. Budapest.',
         body_en="""A nonsurgical facelift that firms and lifts sagging skin.

## How it works

During radio frequency (RF) skin tightening we use an electromagnetic device combined with infrared and vacuum that generates heat to stimulate the production of collagen, elastin and new skin cells.

## Results

The results are temporary, but they are similar to a surgical facelift.""",
         body_hu="""Kellemes, pihentető arckezelés.

## Hogyan működik?

A kezelés során olyan gépi technológiát alkalmazunk, mely egyesíti a rádiófrekvencia, az infravörös fény és a vákuum jótékony hatásait."""),

    dict(match='brazilift', slug_en='brazilift-en', slug_hu='brazilift', gallery_category='brazilift',
         meta_title_en='Brazilift – Brazilian butt and breast lift in Budapest',
         meta_title_hu='Brazilift – fenék- és mellkezelés Budapesten',
         meta_description_en='Brazilift: our buttocks and breast treatment with vacuum for a more plumped, tighter body. Painless Brazilian lift at Infinite Care Beauty Clinic, Budapest.',
         meta_description_hu='Egyedülállóan új fenék- és mellkezelés: vákuumkezeléssel fokozzuk a vér- és nyirokáramlást, így a popsi vagy a mell tónusosabbá, feszesebbé válik. Budapest.',
         body_en="""Our brand new buttocks and breast treatment that makes the body more plumped and tighter with vacuum.

## How it works

The painless vacuum treatment boosts blood and lymph circulation in the treated area.

## Results

- Tighter, more toned buttocks
- More plumped breasts""",
         body_hu="""Egyedülállóan új fenék- és mellkezelés.

## Hogyan működik?

Vákuumkezeléssel fokozzuk a vér- és nyirokáramlást.

## Eredmény

- A popsi tónusosabbá, feszesebbé válik
- A mell tónusosabbá, feszesebbé válik"""),
]

FIELDS = ('slug_en', 'slug_hu', 'meta_title_en', 'meta_title_hu', 'meta_description_en', 'meta_description_hu',
          'body_en', 'body_hu', 'gallery_category')


def fill(Service):
    """Fill the empty page fields of the existing services (by English title keyword). Returns how many were updated."""
    n = 0
    used = set(Service.objects.exclude(slug_en='').values_list('slug_en', flat=True)) | \
        set(Service.objects.exclude(slug_hu='').values_list('slug_hu', flat=True))
    for s in Service.objects.all().order_by('order', 'id'):
        page = next((p for p in PAGES if p['match'] in s.title_en.lower()), None)
        if not page:
            continue
        changed = []
        for f in FIELDS:
            if getattr(s, f):
                continue
            if f.startswith('slug') and page[f] in used:
                continue
            setattr(s, f, page[f])
            changed.append(f)
            if f.startswith('slug'):
                used.add(page[f])
        if changed:
            s.save(update_fields=changed)
            n += 1
    return n
