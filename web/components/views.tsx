import { Fragment } from "react";
import type { Lang } from "@/lib/config";
import { UI } from "@/lib/ui";
import { pagePath } from "@/lib/urls";
import type {
  BlogPost,
  BlogSummary,
  GalleryPhoto,
  HomeContent,
  Service,
  SiteSettings,
  Social,
  VideoClip,
  YouTubeClip,
} from "@/lib/types";
import { BookBand, BookLink, PostCta, SiteShell, SocialIcons } from "./chrome";
import { BlogCard, BodyBlocks, Feature, GalleryGrid, ServiceCard, Subhero, YouTube } from "./media";

export function HomeView({
  lang,
  site,
  socials,
  home,
  gallery,
  clips,
  youtube,
  filters,
}: {
  lang: Lang;
  site: SiteSettings;
  socials: Social[];
  home: HomeContent;
  gallery: GalleryPhoto[];
  clips: VideoClip[];
  youtube: YouTubeClip[];
  filters: [string, string][];
}) {
  const ui = UI[lang];
  const galleryVideos = youtube.filter((v) => v.gallery);
  const watchFeatured = youtube.find((v) => v.featured);
  const watchShorts = youtube.filter((v) => v.home && !v.featured).slice(0, 4);
  return (
    <SiteShell lang={lang} navKey="index" site={site} socials={socials} ui={ui} switchUrls={{ en: "/", hu: "/hu/" }}>
      <section className="hero">
        <div className="hero-bg" data-parallax>
          <img src={home.hero_image} alt="" fetchPriority="high" decoding="async" />
        </div>
        <div className="hero-veil"></div>
        <div className="hero-in">
          <img className="hero-logo" src="/assets/images/infinitecare-logo-4.png" alt="" width={248} height={260} />
          <span className="script hero-script">{home.hello}</span>
          <h1 className="split">
            {home.h1_main}
            {home.h1_em ? (
              <>
                <br />
                <em>{home.h1_em}</em>
              </>
            ) : null}
          </h1>
          <p className="lead reveal in">{home.lead}</p>
          <div className="hero-btns reveal in">
            <a className="btn" href={pagePath(lang, "services")}>
              {ui.nav[1]}
            </a>
            <a className="btn btn-ghost" href="#contact">
              {home.contact_eyebrow}
            </a>
          </div>
        </div>
        <div className="scroll-hint">
          <span></span>
        </div>
      </section>
      {home.marquee?.length ? (
        <section className="marquee">
          <div className="marquee-track">
            {[...home.marquee, ...home.marquee].map((w, i) => (
              <Fragment key={i}>
                <span>{w}</span>
                <i>✦</i>
              </Fragment>
            ))}
          </div>
        </section>
      ) : null}
      <Feature f={home.f1} rev={false} href={pagePath(lang, "services")} />
      {home.counters?.length ? (
        <section className="stats wrap">
          {home.counters.map((c, i) => (
            <div key={i} className="stat reveal">
              <b data-count={c.value} data-suffix={c.suffix}>
                0
              </b>
              <span>{c.label}</span>
            </div>
          ))}
        </section>
      ) : null}
      <Feature f={home.f2} rev={true} href={pagePath(lang, "services")} />
      <BookBand site={site} ui={ui} />
      {gallery.length || galleryVideos.length ? (
        <section className="gallery wrap" id="gallery">
          <div className="g-head">
            <span className="eyebrow reveal">{ui.gal_eyebrow}</span>
            <h2 className="split">{ui.gal_title}</h2>
            <p className="reveal">{ui.gal_text}</p>
            <div className="g-filters reveal" role="group" aria-label={ui.gal_eyebrow}>
              {filters.map(([key, label], i) => (
                <button
                  key={key}
                  type="button"
                  data-filter={key}
                  className={i === 0 ? "on" : undefined}
                  aria-pressed={i === 0}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <p className="g-status" role="status" aria-live="polite" data-tpl={ui.gal_count}></p>
          <GalleryGrid photos={gallery} videos={galleryVideos} ui={ui} />
        </section>
      ) : null}
      {clips.length ? (
        <section className="reels">
          <div className="wrap reel-wrap">
            <div className="reel-text">
              <span className="eyebrow light reveal">{ui.reel_eyebrow}</span>
              <h2 className="split">{ui.reel_title}</h2>
              <p className="reveal">{ui.reel_text}</p>
            </div>
            <div className="reel-grid">
              {clips.map((c) => (
                <figure key={c.id} className="reel reveal">
                  <video muted loop playsInline preload="none" poster={c.poster} aria-label={c.title} data-reel="">
                    <source src={c.video} type="video/mp4" />
                  </video>
                  <button type="button" className="reel-btn" aria-label={ui.lb.play}></button>
                  <figcaption>{c.title}</figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>
      ) : null}
      {watchFeatured || watchShorts.length ? (
        <section className="watch wrap" id="watch">
          <div className="w-top">
            {watchFeatured ? (
              <div className="w-main reveal">
                <YouTube v={watchFeatured} ui={ui} />
              </div>
            ) : null}
            <div className="w-text">
              <span className="eyebrow reveal">{ui.yt_eyebrow}</span>
              <h2 className="split">{ui.yt_title}</h2>
              <p className="reveal">{ui.yt_text}</p>
              {site.youtube ? (
                <a className="btn reveal" href={site.youtube} rel="noopener me">
                  {ui.yt_sub}
                </a>
              ) : null}
            </div>
          </div>
          {watchShorts.length ? (
            <div className="w-shorts">
              {watchShorts.map((v) => (
                <div key={v.id} className="reveal">
                  <YouTube v={v} ui={ui} />
                </div>
              ))}
            </div>
          ) : null}
        </section>
      ) : null}
      <section className="cta">
        <div className="cta-bg" data-parallax>
          <img src={home.cta_image} alt="" loading="lazy" decoding="async" />
        </div>
        <div className="cta-in">
          <span className="script reveal">{home.cta_script}</span>
          <h2 className="split">{home.cta_title}</h2>
          <a className="btn reveal" href={site.phone_href} data-s="tel">
            {home.cta_button}
          </a>
        </div>
      </section>
      <section className="contact wrap" id="contact">
        <div className="c-info">
          <span className="eyebrow reveal">{home.contact_eyebrow}</span>
          <h2 className="split">{home.contact_title}</h2>
          <p className="reveal">{home.contact_text}</p>
          {site.booking_url ? (
            <div className="c-book reveal">
              <BookLink site={site} ui={ui} label={ui.book_online} cls="" />
              <span>
                {ui.bk_call}{" "}
                <a href={site.phone_href} data-s="phone">
                  {site.phone}
                </a>
              </span>
            </div>
          ) : null}
          {socials.length ? (
            <div className="c-social reveal">
              <span>{ui.follow}</span>
              <div className="social">
                <SocialIcons socials={socials} />
              </div>
            </div>
          ) : null}
          <form
            className="cform reveal"
            id="contact-form"
            noValidate
            data-ok={ui.ok}
            data-err={ui.err}
            data-sending={ui.sending}
            data-invalid={ui.inv}
            data-mailto={site.email}
            data-s="mailto"
            {...{ toolname: "send_message", tooldescription: ui.form_tool }}
          >
            <label>
              <input name="name" required maxLength={100} placeholder=" " autoComplete="name" {...{ toolparamdescription: ui.form[0] }} />
              <span>{ui.form[0]}</span>
            </label>
            <label>
              <input name="email" type="email" required maxLength={200} placeholder=" " autoComplete="email" {...{ toolparamdescription: ui.form[1] }} />
              <span>{ui.form[1]}</span>
            </label>
            <label>
              <input name="phone" type="tel" maxLength={40} placeholder=" " autoComplete="tel" {...{ toolparamdescription: ui.form[2] }} />
              <span>{ui.form[2]}</span>
            </label>
            <label>
              <textarea name="message" rows={4} required maxLength={5000} placeholder=" " {...{ toolparamdescription: ui.form[3] }}></textarea>
              <span>{ui.form[3]}</span>
            </label>
            <div className="hp" aria-hidden="true">
              <input name="website" tabIndex={-1} autoComplete="off" />
            </div>
            <button className="btn" type="submit">
              {ui.form[4]}
            </button>
            <p className="form-status" role="status" aria-live="polite"></p>
          </form>
        </div>
        {home.contact_image || site.map_embed ? (
          <div className="c-side">
            {home.contact_image ? (
              <figure className="c-photo reveal-img">
                <img src={home.contact_image} alt={ui.entrance} loading="lazy" decoding="async" />
                <figcaption>
                  <b>{ui.find_us}</b>
                  <span data-s="addrcity">
                    {site.address}, {site.city}
                  </span>
                </figcaption>
              </figure>
            ) : null}
            {site.map_embed ? (
              <div className="map reveal-img" data-s="map" data-map={site.map_embed} data-title={ui.map_title}>
                <div className="map-fb">
                  <svg className="map-pin" viewBox="0 0 24 24" width="40" height="40" aria-hidden="true" focusable="false">
                    <path
                      fill="currentColor"
                      d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"
                    />
                  </svg>
                  <p className="map-addr" data-s="addrcity">
                    {site.address}, {site.city}
                  </p>
                  <button type="button" className="btn map-btn">
                    {ui.map_show}
                  </button>
                  <small>{ui.map_note}</small>
                  <a
                    className="link"
                    data-s="maplink"
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(site.address + ", " + site.city)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {ui.map_open}
                  </a>
                </div>
              </div>
            ) : null}
          </div>
        ) : null}
      </section>
    </SiteShell>
  );
}

export function ServicesView({
  lang,
  site,
  socials,
  services,
}: {
  lang: Lang;
  site: SiteSettings;
  socials: Social[];
  services: Service[];
}) {
  const ui = UI[lang];
  return (
    <SiteShell
      lang={lang}
      navKey="services"
      site={site}
      socials={socials}
      ui={ui}
      switchUrls={{ en: pagePath("en", "services"), hu: pagePath("hu", "services") }}
    >
      <Subhero
        heroImage="/assets/images/services.webp"
        kicker="Beauty Clinic"
        title={ui.titles.services}
        site={site}
        fetchPriority
      />
      <main className="svcs">
        <div className="svlist">
          {services.map((s, i) => (
            <ServiceCard key={s.id} s={s} n={i + 1} site={site} ui={ui} />
          ))}
        </div>
        <BookBand site={site} ui={ui} />
      </main>
    </SiteShell>
  );
}

export function BlogIndexView({
  lang,
  site,
  socials,
  posts,
}: {
  lang: Lang;
  site: SiteSettings;
  socials: Social[];
  posts: BlogSummary[];
}) {
  const ui = UI[lang];
  return (
    <SiteShell
      lang={lang}
      navKey="blog"
      site={site}
      socials={socials}
      ui={ui}
      switchUrls={{ en: pagePath("en", "blog"), hu: pagePath("hu", "blog") }}
    >
      <Subhero
        heroImage="/assets/images/gallery/clinic-lounge.webp"
        kicker="Beauty Clinic"
        title={ui.titles.blog}
        site={site}
        fetchPriority
      />
      <main className="blog">
        <div className="wrap">
          <span className="eyebrow reveal">{ui.blog_eyebrow}</span>
          <h2 className="split">{ui.blog_lead}</h2>
          {posts.length ? (
            <div className="bgrid">
              {posts.map((p) => (
                <BlogCard key={p.slug} p={p} ui={ui} />
              ))}
            </div>
          ) : (
            <p className="b-empty">{ui.empty}</p>
          )}
        </div>
      </main>
    </SiteShell>
  );
}

export function BlogPostView({
  lang,
  site,
  socials,
  post,
  more,
}: {
  lang: Lang;
  site: SiteSettings;
  socials: Social[];
  post: BlogPost;
  more: BlogSummary[];
}) {
  const ui = UI[lang];
  return (
    <SiteShell
      lang={lang}
      navKey="blog"
      site={site}
      socials={socials}
      ui={ui}
      switchUrls={{ en: pagePath("en", "blog", post.slug), hu: pagePath("hu", "blog", post.slug) }}
    >
      <Subhero heroImage={post.cover} kicker={post.date} title={post.title} site={site} fetchPriority />
      <main className="post">
        <article className="wrap post-in">
          <div className="pbody">
            <BodyBlocks blocks={post.blocks} linkified />
            {post.videos?.map((v) => (
              <figure key={v.id} className="post-vid">
                <YouTube v={v} ui={ui} />
              </figure>
            ))}
          </div>
          <p className="post-note">{ui.post_note}</p>
          <PostCta site={site} ui={ui} />
          <a className="post-back" href={pagePath(lang, "blog")}>
            {ui.back}
          </a>
        </article>
        {more.length ? (
          <section className="post-more">
            <div className="wrap">
              <h3>{ui.more}</h3>
              <div className="bgrid">
                {more.map((p) => (
                  <BlogCard key={p.slug} p={p} ui={ui} />
                ))}
              </div>
            </div>
          </section>
        ) : null}
      </main>
    </SiteShell>
  );
}

export function ServiceLandingView({
  lang,
  site,
  socials,
  svc,
  photos,
  others,
}: {
  lang: Lang;
  site: SiteSettings;
  socials: Social[];
  svc: Service;
  photos: GalleryPhoto[];
  others: { title: string; href: string }[];
}) {
  const ui = UI[lang];
  return (
    <SiteShell
      lang={lang}
      navKey="services"
      site={site}
      socials={socials}
      ui={ui}
      switchUrls={{
        en: svc.slugs.en ? `/${svc.slugs.en}` : pagePath("en", "services"),
        hu: svc.slugs.hu ? `/${svc.slugs.hu}` : pagePath("hu", "services"),
      }}
    >
      <Subhero heroImage={svc.image} kicker={svc.eyebrow} title={svc.title} site={site} fetchPriority />
      <main className="post spage">
        <article className="wrap post-in">
          <nav className="crumbs" aria-label="Breadcrumb">
            <a href={pagePath(lang, "index")}>{ui.nav[0]}</a> / <a href={pagePath(lang, "services")}>{ui.nav[1]}</a> /{" "}
            <span aria-current="page">{svc.title}</span>
          </nav>
          <div className="pbody">
            <p className="sp-lead">
              {svc.description.map((l, i) => (
                <span key={i}>
                  {i ? <br /> : null}
                  {l}
                </span>
              ))}
            </p>
            <BodyBlocks blocks={svc.blocks} />
            {svc.videos?.length ? (
              <>
                <h2>{ui.svc_videos}</h2>
                <div className="svc-vids">
                  {svc.videos.map((v) => (
                    <YouTube key={v.id} v={v} ui={ui} />
                  ))}
                </div>
              </>
            ) : null}
          </div>
          <PostCta site={site} ui={ui} />
        </article>
        {photos.length ? (
          <section className="sp-gal">
            <div className="wrap">
              <h2>{ui.svc_photos}</h2>
              <GalleryGrid photos={photos} videos={[]} ui={ui} />
            </div>
          </section>
        ) : null}
        {others.length ? (
          <nav className="sp-others wrap" aria-label={ui.svc_others}>
            <h3>{ui.svc_others}</h3>
            <ul>
              {others.map((o) => (
                <li key={o.href}>
                  <a href={o.href}>{o.title}</a>
                </li>
              ))}
            </ul>
            <a className="post-back" href={pagePath(lang, "services")}>
              {ui.svc_back}
            </a>
          </nav>
        ) : null}
      </main>
    </SiteShell>
  );
}
