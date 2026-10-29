import { SITE_ORIGIN, type Lang } from "./config";

export function langPrefix(lang: Lang) {
  return lang === "hu" ? "/hu" : "";
}

export function pagePath(lang: Lang, name: "index" | "services" | "blog", slug?: string) {
  const pre = langPrefix(lang);
  if (slug) return `${pre}/blog/${slug}`;
  if (name === "index") return pre ? `${pre}/` : "/";
  return `${pre}/${name}`;
}

export function servicePath(slug: string) {
  return `/${slug}`;
}

export function abs(path: string) {
  if (path.startsWith("http")) return path;
  return SITE_ORIGIN + (path.startsWith("/") ? path : `/${path}`);
}

export function blogPostPath(lang: Lang, slug: string) {
  return pagePath(lang, "blog", slug);
}

export function switchPaths(
  lang: Lang,
  kind: "index" | "services" | "blog" | "blog_post" | "service",
  opts?: { slug?: string; slugs?: { en: string; hu: string } },
) {
  if (kind === "service" && opts?.slugs) {
    return {
      en: opts.slugs.en ? servicePath(opts.slugs.en) : pagePath("en", "services"),
      hu: opts.slugs.hu ? servicePath(opts.slugs.hu) : pagePath("hu", "services"),
    };
  }
  if (kind === "blog_post" && opts?.slug) {
    return { en: blogPostPath("en", opts.slug), hu: blogPostPath("hu", opts.slug) };
  }
  const name = kind === "blog_post" ? "blog" : kind === "service" ? "services" : kind;
  return { en: pagePath("en", name), hu: pagePath("hu", name) };
}
