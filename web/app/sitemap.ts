import type { MetadataRoute } from "next";
import { getBlog, getServices } from "@/lib/api";
import { abs, pagePath, servicePath } from "@/lib/urls";

export const revalidate = 180;

function pair(en: string, hu: string, lastmod?: string): MetadataRoute.Sitemap[number][] {
  const langs = {
    en: abs(en),
    hu: abs(hu),
    "x-default": abs(en),
  };
  return [
    { url: abs(en), lastModified: lastmod, alternates: { languages: langs } },
    { url: abs(hu), lastModified: lastmod, alternates: { languages: langs } },
  ];
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [posts, services] = await Promise.all([getBlog("en"), getServices("en")]);
  const urls: MetadataRoute.Sitemap = [
    ...pair(pagePath("en", "index"), pagePath("hu", "index")),
    ...pair(pagePath("en", "services"), pagePath("hu", "services")),
    ...pair(pagePath("en", "blog"), pagePath("hu", "blog")),
  ];
  for (const p of posts) {
    urls.push(
      ...pair(pagePath("en", "blog", p.slug), pagePath("hu", "blog", p.slug), p.iso_date),
    );
  }
  const seen = new Set<string>();
  for (const s of services) {
    if (!s.slugs.en || !s.slugs.hu) continue;
    const key = `${s.slugs.en}|${s.slugs.hu}`;
    if (seen.has(key)) continue;
    seen.add(key);
    urls.push(...pair(servicePath(s.slugs.en), servicePath(s.slugs.hu), s.updated));
  }
  return urls;
}
