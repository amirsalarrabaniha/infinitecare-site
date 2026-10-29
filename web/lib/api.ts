import { API_ORIGIN, REVALIDATE_SECONDS, type Lang } from "./config";
import { blogPostPath, servicePath } from "./urls";
import { UI } from "./ui";
import type {
  BlogPost,
  BlogSummary,
  GalleryPayload,
  HomeContent,
  Service,
  SiteSettings,
  Social,
} from "./types";

import settingsEn from "./fallback/settings-en.json";
import settingsHu from "./fallback/settings-hu.json";
import homeEn from "./fallback/home-en.json";
import homeHu from "./fallback/home-hu.json";
import servicesEn from "./fallback/services-en.json";
import servicesHu from "./fallback/services-hu.json";
import galleryEn from "./fallback/gallery-en.json";
import galleryHu from "./fallback/gallery-hu.json";
import blogEn from "./fallback/blog-en.json";
import blogHu from "./fallback/blog-hu.json";
import postsEn from "./fallback/posts-en.json";
import postsHu from "./fallback/posts-hu.json";

const SOCIAL_NAMES = {
  facebook: "Facebook",
  instagram: "Instagram",
  youtube: "YouTube",
  tiktok: "TikTok",
} as const;

async function apiGet<T>(path: string, fallback: T): Promise<T> {
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 8000);
    const res = await fetch(`${API_ORIGIN}${path}`, {
      next: { revalidate: REVALIDATE_SECONDS },
      headers: { Accept: "application/json", "User-Agent": "infinitecare-next/1.0" },
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error(String(res.status));
    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("json")) throw new Error("not-json");
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getSettings(lang: Lang): Promise<SiteSettings> {
  const fb = (lang === "hu" ? settingsHu : settingsEn) as SiteSettings;
  return apiGet(`/api/settings/?lang=${lang}`, fb);
}

export async function getHome(lang: Lang): Promise<HomeContent> {
  const fb = (lang === "hu" ? homeHu : homeEn) as HomeContent;
  return apiGet(`/api/home/?lang=${lang}`, fb);
}

export async function getServices(lang: Lang): Promise<Service[]> {
  const fb = (lang === "hu" ? servicesHu : servicesEn) as { results: Service[] };
  const data = await apiGet(`/api/services/?lang=${lang}`, fb);
  return (data.results || []).map((s) => ({
    ...s,
    href: s.slug ? servicePath(s.slug) : "",
  }));
}

export async function getGallery(lang: Lang): Promise<GalleryPayload> {
  const fb = (lang === "hu" ? galleryHu : galleryEn) as GalleryPayload;
  return apiGet(`/api/gallery/?lang=${lang}`, fb);
}

export async function getBlog(lang: Lang): Promise<BlogSummary[]> {
  const fb = (lang === "hu" ? blogHu : blogEn) as { results: BlogSummary[] };
  const data = await apiGet(`/api/blog/?lang=${lang}`, fb);
  return (data.results || []).map((p) => ({ ...p, url: blogPostPath(lang, p.slug) }));
}

export async function getPost(lang: Lang, slug: string): Promise<BlogPost | null> {
  const pack = (lang === "hu" ? postsHu : postsEn) as Record<string, BlogPost>;
  const fb = pack[slug];
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 8000);
    const res = await fetch(`${API_ORIGIN}/api/blog/${encodeURIComponent(slug)}/?lang=${lang}`, {
      next: { revalidate: REVALIDATE_SECONDS },
      headers: { Accept: "application/json", "User-Agent": "infinitecare-next/1.0" },
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(String(res.status));
    const post = (await res.json()) as BlogPost;
    return { ...post, url: blogPostPath(lang, post.slug) };
  } catch {
    return fb ? { ...fb, url: blogPostPath(lang, fb.slug) } : null;
  }
}

export function socialsFrom(site: SiteSettings, lang: Lang): Social[] {
  const out: Social[] = [];
  for (const [key, name] of Object.entries(SOCIAL_NAMES) as [keyof typeof SOCIAL_NAMES, string][]) {
    const url = site[key];
    if (url) out.push({ key, name, url, label: UI[lang].soc.replace("{name}", name) });
  }
  return out;
}

export function galleryFilters(
  items: { cats: string }[],
  lang: Lang,
): [string, string][] {
  const used = new Set(items.flatMap((g) => g.cats.split(/\s+/).filter(Boolean)));
  return UI[lang].gal_filters.filter(([k]) => k === "all" || used.has(k));
}

export async function findServiceBySlug(slug: string): Promise<{ service: Service; lang: Lang } | null> {
  const [en, hu] = await Promise.all([getServices("en"), getServices("hu")]);
  const enHit = en.find((s) => s.slug === slug);
  if (enHit) return { service: enHit, lang: "en" };
  const huHit = hu.find((s) => s.slug === slug);
  if (huHit) return { service: huHit, lang: "hu" };
  return null;
}

export async function allServiceSlugs(): Promise<{ slug: string; lang: Lang }[]> {
  const [en, hu] = await Promise.all([getServices("en"), getServices("hu")]);
  const out: { slug: string; lang: Lang }[] = [];
  for (const s of en) if (s.slugs.en) out.push({ slug: s.slugs.en, lang: "en" });
  for (const s of hu) if (s.slugs.hu) out.push({ slug: s.slugs.hu, lang: "hu" });
  return out;
}
