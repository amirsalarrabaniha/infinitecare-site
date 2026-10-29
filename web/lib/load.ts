import type { Metadata } from "next";
import type { Lang } from "./config";
import { UI } from "./ui";
import { pagePath, abs, servicePath } from "./urls";
import { SITE_NAME } from "./config";
import {
  findServiceBySlug,
  galleryFilters,
  getBlog,
  getGallery,
  getHome,
  getPost,
  getServices,
  getSettings,
  socialsFrom,
} from "./api";
import { blogJsonLd, buildMetadata, orgJsonLd, serviceJsonLd, toLd } from "./seo";

export const revalidate = 180;

export async function loadChrome(lang: Lang) {
  const site = await getSettings(lang);
  return { site, socials: socialsFrom(site, lang), ui: UI[lang] };
}

export async function loadHome(lang: Lang) {
  const [{ site, socials, ui }, home, gallery] = await Promise.all([
    loadChrome(lang),
    getHome(lang),
    getGallery(lang),
  ]);
  const items = [...gallery.photos, ...gallery.youtube.filter((v) => v.gallery)];
  return {
    lang,
    site,
    socials,
    ui,
    home,
    gallery: gallery.photos,
    clips: gallery.videos,
    youtube: gallery.youtube,
    filters: galleryFilters(items, lang),
    ld: orgJsonLd(site, socials, lang, ui.book_online),
  };
}

export async function loadServices(lang: Lang) {
  const [{ site, socials, ui }, services] = await Promise.all([loadChrome(lang), getServices(lang)]);
  return { lang, site, socials, ui, services };
}

export async function loadBlog(lang: Lang) {
  const [{ site, socials, ui }, posts] = await Promise.all([loadChrome(lang), getBlog(lang)]);
  return { lang, site, socials, ui, posts };
}

export async function loadPost(lang: Lang, slug: string) {
  const [{ site, socials, ui }, post, posts] = await Promise.all([
    loadChrome(lang),
    getPost(lang, slug),
    getBlog(lang),
  ]);
  if (!post) return null;
  const more = posts.filter((p) => p.slug !== slug).slice(0, 2);
  const og = post.cover;
  return {
    lang,
    site,
    socials,
    ui,
    post,
    more,
    og,
    ld: blogJsonLd(post, lang, socials, og),
  };
}

export async function loadService(slug: string) {
  const hit = await findServiceBySlug(slug);
  if (!hit) return null;
  const { service, lang } = hit;
  const [{ site, socials, ui }, services, gallery] = await Promise.all([
    loadChrome(lang),
    getServices(lang),
    getGallery(lang),
  ]);
  const photos = service.gallery_category
    ? gallery.photos.filter((g) => g.category === service.gallery_category).slice(0, 9)
    : [];
  const others = services
    .filter((x) => x.slug && x.id !== service.id)
    .map((x) => ({ title: x.title, href: servicePath(x.slug) }));
  const canonical = servicePath(service.slug);
  const switchUrls = {
    en: service.slugs.en ? servicePath(service.slugs.en) : pagePath("en", "services"),
    hu: service.slugs.hu ? servicePath(service.slugs.hu) : pagePath("hu", "services"),
  };
  return {
    lang,
    site,
    socials,
    ui,
    svc: service,
    photos,
    others,
    canonical,
    switchUrls,
    ld: serviceJsonLd(
      lang,
      service,
      site,
      canonical,
      pagePath(lang, "index"),
      pagePath(lang, "services"),
      [...ui.nav],
    ),
  };
}

export function homeMeta(lang: Lang, description: string): Metadata {
  const alts = { en: pagePath("en", "index"), hu: pagePath("hu", "index") };
  return buildMetadata({
    lang,
    title: UI[lang].titles.index,
    description,
    canonical: alts[lang],
    alternates: alts,
  });
}

export function servicesMeta(lang: Lang, description: string): Metadata {
  const alts = { en: pagePath("en", "services"), hu: pagePath("hu", "services") };
  return buildMetadata({
    lang,
    title: UI[lang].titles.services,
    description,
    canonical: alts[lang],
    alternates: alts,
    ogImage: abs("/assets/images/services.webp"),
  });
}

export function blogMeta(lang: Lang): Metadata {
  const alts = { en: pagePath("en", "blog"), hu: pagePath("hu", "blog") };
  return buildMetadata({
    lang,
    title: UI[lang].titles.blog,
    description: UI[lang].blog_desc,
    canonical: alts[lang],
    alternates: alts,
    ogImage: abs("/assets/images/gallery/clinic-lounge.webp"),
  });
}

export function postMeta(
  lang: Lang,
  post: { title: string; excerpt: string; slug: string; cover: string; iso_date: string },
): Metadata {
  const alts = { en: pagePath("en", "blog", post.slug), hu: pagePath("hu", "blog", post.slug) };
  return {
    ...buildMetadata({
      lang,
      title: `${post.title} | ${SITE_NAME}`,
      description: post.excerpt,
      canonical: alts[lang],
      alternates: alts,
      ogType: "article",
      ogImage: post.cover,
      published: post.iso_date,
    }),
    title: `${post.title} | ${SITE_NAME}`,
  };
}

export { toLd };
