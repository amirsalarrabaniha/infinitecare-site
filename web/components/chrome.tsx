import type { Lang } from "@/lib/config";
import type { SiteSettings, Social } from "@/lib/types";
import type { UICopy } from "@/lib/ui";
import { pagePath } from "@/lib/urls";
import { SOCIAL_ICONS } from "./icons";

export function BookLink({
  site,
  ui,
  label,
  cls,
}: {
  site: SiteSettings;
  ui: UICopy;
  label: string;
  cls: string;
}) {
  if (!site.booking_url) return null;
  return (
    <a className={`btn ${cls}`} href={site.booking_url} target="_blank" rel="noopener noreferrer" data-s="booking">
      {label}
      <span className="vh"> ({ui.newtab})</span>
    </a>
  );
}

export function SocialIcons({ socials }: { socials: Social[] }) {
  return (
    <>
      {socials.map((s) => (
        <a
          key={s.key}
          data-s={`soc-${s.key}`}
          href={s.url}
          target="_blank"
          rel="noopener noreferrer me"
          aria-label={s.label}
          title={s.name}
        >
          <span dangerouslySetInnerHTML={{ __html: SOCIAL_ICONS[s.key] || "" }} />
        </a>
      ))}
    </>
  );
}

export function SiteShell({
  lang,
  navKey,
  site,
  socials,
  ui,
  switchUrls,
  children,
}: {
  lang: Lang;
  navKey: string;
  site: SiteSettings;
  socials: Social[];
  ui: UICopy;
  switchUrls: { en: string; hu: string };
  children: React.ReactNode;
}) {
  const nav = [
    { key: "index", label: ui.nav[0], href: pagePath(lang, "index") },
    { key: "services", label: ui.nav[1], href: pagePath(lang, "services") },
    ...(site.offers_url
      ? [{ key: "offers", label: ui.nav[2], href: site.offers_url, external: true }]
      : []),
    { key: "blog", label: ui.nav[3], href: pagePath(lang, "blog") },
  ];
  return (
    <>
      <header className="nav">
        <a href={pagePath(lang, "index")} className="brand">
          <img className="logo-light" src="/assets/images/infinitecare-logo-2.png" alt="Infinite Care" width={240} height={120} />
          <img className="logo-dark" src="/assets/images/infinitecare-logo-1.png" alt="Infinite Care" width={280} height={105} />
        </a>
        <nav className="menu">
          {nav.map((n) => (
            <a
              key={n.key}
              href={n.href}
              className={n.key === navKey ? "active" : ""}
              {...(n.external ? { target: "_blank", rel: "noopener noreferrer", "data-s": "offers" } : {})}
            >
              {n.label}
              {n.external ? <span className="vh"> ({ui.newtab})</span> : null}
            </a>
          ))}
          <div className="langsw" role="group" aria-label="Language">
            <a
              href={switchUrls.en}
              hrefLang="en"
              lang="en"
              data-lang="en"
              className={lang === "en" ? "on" : ""}
              {...(lang === "en" ? { "aria-current": "true" as const } : {})}
            >
              EN
            </a>
            <a
              href={switchUrls.hu}
              hrefLang="hu"
              lang="hu"
              data-lang="hu"
              className={lang === "hu" ? "on" : ""}
              {...(lang === "hu" ? { "aria-current": "true" as const } : {})}
            >
              HU
            </a>
          </div>
          {site.booking_url ? <BookLink site={site} ui={ui} label={ui.book_now} cls="btn-sm menu-book" /> : null}
          <a className="menu-tel" href={site.phone_href} data-s="phone">
            {site.phone}
          </a>
        </nav>
        {site.booking_url ? (
          <BookLink site={site} ui={ui} label={ui.book_now} cls="btn-sm nav-cta" />
        ) : (
          <a className="btn btn-sm nav-cta" href={site.phone_href} data-s="phone">
            {site.phone}
          </a>
        )}
        <button className="burger" aria-label={ui.menu}>
          <span></span>
          <span></span>
        </button>
      </header>
      {children}
      <footer className="footer">
        <div className="wrap fgrid">
          <div className="reveal">
            <img src="/assets/images/infinitecare-logo-2.png" alt="Infinite Care" className="flogo" width={240} height={120} loading="lazy" />
            <p className="script">Beauty Clinic</p>
            <p className="flinks">
              {nav
                .filter((n) => n.key !== "offers")
                .map((n) => (
                  <a key={n.key} href={n.href}>
                    {n.label}
                  </a>
                ))}
            </p>
          </div>
          <div className="reveal">
            <h3>{ui.hours}</h3>
            <p data-s="hours">
              {site.hours.map((l, i) => (
                <span key={i}>
                  {i ? <br /> : null}
                  {l}
                </span>
              ))}
            </p>
          </div>
          <div className="reveal">
            <h3>{ui.res}</h3>
            <p>
              <a href={site.phone_href} data-s="phone">
                {site.phone}
              </a>
              <br />
              <span data-s="address">{site.address}</span>
              <br />
              <a href={`mailto:${site.email}`} data-s="email">
                {site.email}
              </a>
            </p>
          </div>
          <div className="reveal">
            <h3>{ui.follow}</h3>
            <div className="social">
              <SocialIcons socials={socials} />
            </div>
          </div>
        </div>
        <div className="wrap fbottom">
          <span data-s="city">{site.city}</span>
          <span data-s="tagline">{site.tagline}</span>
        </div>
      </footer>
    </>
  );
}

export function BookBand({ site, ui }: { site: SiteSettings; ui: UICopy }) {
  if (!site.booking_url) return null;
  return (
    <section className="bookband wrap reveal" id="book-online">
      <div className="bb-in">
        <div className="bb-t">
          <span className="eyebrow">{ui.bk_eyebrow}</span>
          <h2>{ui.bk_title}</h2>
          <p>{ui.bk_text}</p>
        </div>
        <div className="bb-act">
          <BookLink site={site} ui={ui} label={ui.book_online} cls="" />
          <p>
            {ui.bk_call}{" "}
            <a href={site.phone_href} data-s="phone">
              {site.phone}
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}

export function PostCta({ site, ui }: { site: SiteSettings; ui: UICopy }) {
  return (
    <div className="post-cta">
      <h3>{ui.book_cta}</h3>
      <div className="pc-btns">
        {site.booking_url ? <BookLink site={site} ui={ui} label={ui.book_online} cls="pc-book" /> : null}
        <a className="btn pc-tel" href={site.phone_href} data-s="phone">
          {site.phone}
        </a>
      </div>
    </div>
  );
}
