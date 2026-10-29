import type { FeatureBlock, GalleryPhoto, YouTubeClip, BlogSummary, SiteSettings } from "@/lib/types";
import type { UICopy } from "@/lib/ui";
import { brk, faqMark, linkify } from "@/lib/linkify";
import type { BodyBlock } from "@/lib/types";
import { BookLink } from "./chrome";

export function YouTube({ v, ui }: { v: YouTubeClip; ui: UICopy }) {
  return (
    <div className={`yt ${v.vertical ? "yt-v" : "yt-w"}`} data-yt={v.youtube_id} data-title={v.title}>
      <button type="button" className="yt-btn" aria-label={`${ui.yt_play}: ${v.title}`}>
        <img
          src={v.poster}
          alt=""
          width={v.width || undefined}
          height={v.height || undefined}
          loading="lazy"
          decoding="async"
        />
        <strong className="yt-t">{v.title}</strong>
      </button>
      {v.caption ? <small className="yt-c">{v.caption}</small> : null}
    </div>
  );
}

export function Subhero({
  heroImage,
  kicker,
  title,
  site,
  fetchPriority,
}: {
  heroImage: string;
  kicker: string;
  title: string;
  site: SiteSettings;
  fetchPriority?: boolean;
}) {
  return (
    <section className="subhero">
      <div className="subhero-bg" data-parallax>
        <img src={heroImage} alt="" fetchPriority={fetchPriority ? "high" : undefined} decoding="async" />
      </div>
      <div className="subhero-in">
        <span className="script reveal in">{kicker || "Beauty Clinic"}</span>
        <h1 className="split">{title}</h1>
        <a className="btn reveal in" href={site.phone_href} data-s="phone">
          {site.phone}
        </a>
      </div>
    </section>
  );
}

export function Feature({
  f,
  rev,
  href,
}: {
  f: FeatureBlock;
  rev: boolean;
  href: string;
}) {
  return (
    <section className={`feature ${rev ? "feature-rev" : ""} wrap`}>
      <div className="f-img reveal-img">
        <img src={f.image} alt={f.title} loading="lazy" decoding="async" data-tilt="" />
      </div>
      <div className="f-text">
        <span className="eyebrow reveal">{f.eyebrow}</span>
        <h2 className="split">{f.title}</h2>
        {f.paragraphs.map((p, i) => (
          <p key={i} className="reveal" dangerouslySetInnerHTML={{ __html: brk(p) }} />
        ))}
        {f.button ? (
          <a className="btn reveal" href={href}>
            {f.button}
          </a>
        ) : null}
      </div>
    </section>
  );
}

export function BodyBlocks({ blocks, linkified }: { blocks: BodyBlock[]; linkified?: boolean }) {
  const marked = linkified ? faqMark(blocks) : blocks;
  return (
    <>
      {marked.map((b, i) => {
        if (b.type === "h") return <h2 key={i}>{b.text}</h2>;
        if (b.type === "q") return <h3 key={i} className="faq-q">{b.text}</h3>;
        if (b.type === "ul") {
          return (
            <ul key={i}>
              {b.items.map((item, j) =>
                linkified ? (
                  <li key={j} dangerouslySetInnerHTML={{ __html: linkify(item) }} />
                ) : (
                  <li key={j}>{item}</li>
                ),
              )}
            </ul>
          );
        }
        return linkified ? (
          <p key={i} dangerouslySetInnerHTML={{ __html: linkify(b.text) }} />
        ) : (
          <p key={i}>{b.text}</p>
        );
      })}
    </>
  );
}

export function BlogCard({ p, ui }: { p: BlogSummary; ui: UICopy }) {
  return (
    <article className="bcard reveal">
      <a className="bc-img" href={p.url} tabIndex={-1} aria-hidden="true">
        <img src={p.cover} alt="" loading="lazy" decoding="async" />
      </a>
      <div className="bc-body">
        <time dateTime={p.iso_date}>{p.date}</time>
        <h3>
          <a href={p.url}>{p.title}</a>
        </h3>
        <p>{p.excerpt}</p>
        <a className="bc-more" href={p.url}>
          {ui.read_more}
        </a>
      </div>
    </article>
  );
}

export function GalleryGrid({
  photos,
  videos,
  ui,
}: {
  photos: GalleryPhoto[];
  videos: YouTubeClip[];
  ui: UICopy;
}) {
  return (
    <div
      className="g-grid"
      data-lb-close={ui.lb.close}
      data-lb-prev={ui.lb.prev}
      data-lb-next={ui.lb.next}
    >
      {photos.map((g) => (
        <button
          key={g.id}
          type="button"
          className="g-item reveal"
          data-cat={g.cats}
          data-full={g.image}
          data-caption={g.alt}
        >
          <img
            src={g.image}
            alt={g.alt}
            loading="lazy"
            decoding="async"
            width={g.width || undefined}
            height={g.height || undefined}
          />
          <span>{g.alt}</span>
        </button>
      ))}
      {videos.map((v) => (
        <div key={v.id} className="g-item g-vid reveal" data-cat={v.cats}>
          <YouTube v={v} ui={ui} />
        </div>
      ))}
    </div>
  );
}

export function ServiceCard({
  s,
  n,
  site,
  ui,
}: {
  s: import("@/lib/types").Service;
  n: number;
  site: SiteSettings;
  ui: UICopy;
}) {
  return (
    <article className={`svc wrap ${n % 2 === 0 ? "svc-rev" : ""}`} id={`service-${s.id}`}>
      <div className="f-img reveal-img">
        <img src={s.image} alt={s.title} loading="lazy" decoding="async" data-tilt="" />
        <span className="num">{String(n).padStart(2, "0")}</span>
      </div>
      <div className="f-text">
        <span className="eyebrow reveal">{s.eyebrow}</span>
        <h2 className="split">{s.title}</h2>
        <p className="reveal">
          {s.description.map((l, i) => (
            <span key={i}>
              {i ? <br /> : null}
              {l}
            </span>
          ))}
        </p>
        <div className="reveal btnrow">
          {site.booking_url ? (
            <>
              <BookLink site={site} ui={ui} label={ui.book_online} cls="" />
              <a className="link" href={site.phone_href} data-s="phone">
                {site.phone}
              </a>
            </>
          ) : (
            <a className="btn" href={site.phone_href} data-s="tel">
              {ui.book}
            </a>
          )}
        </div>
        {s.slug ? (
          <p className="reveal svc-more">
            <a className="link" href={s.href}>
              {ui.svc_more} →
            </a>
          </p>
        ) : null}
        {s.videos?.length ? (
          <div className="svc-vids reveal">
            {s.videos.map((v) => (
              <YouTube key={v.id} v={v} ui={ui} />
            ))}
          </div>
        ) : null}
      </div>
    </article>
  );
}
