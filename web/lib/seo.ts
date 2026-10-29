import type { Metadata } from "next";
import { SITE_NAME, SITE_ORIGIN, type Lang } from "./config";
import { abs } from "./urls";
import type { Service, SiteSettings, Social } from "./types";

export function pageTitle(title: string, pageTitleOverride?: string) {
  return pageTitleOverride || `${title} | ${SITE_NAME}`;
}

export function hreflang(alternates: { en: string; hu: string }): Metadata {
  return {
    alternates: {
      canonical: abs(alternates.en === alternates.hu ? alternates.en : ""),
      languages: {
        en: abs(alternates.en),
        hu: abs(alternates.hu),
        "x-default": abs(alternates.en),
      },
    },
  };
}

export function buildMetadata(opts: {
  lang: Lang;
  title: string;
  description: string;
  canonical: string;
  alternates: { en: string; hu: string };
  ogType?: "website" | "article";
  ogImage?: string;
  published?: string;
}): Metadata {
  const title = opts.title.includes("|") ? opts.title : `${opts.title} | ${SITE_NAME}`;
  const canonical = abs(opts.canonical);
  return {
    title,
    description: opts.description,
    alternates: {
      canonical,
      languages: {
        en: abs(opts.alternates.en),
        hu: abs(opts.alternates.hu),
        "x-default": abs(opts.alternates.en),
      },
    },
    openGraph: {
      type: opts.ogType || "website",
      url: canonical,
      siteName: SITE_NAME,
      locale: opts.lang === "hu" ? "hu_HU" : "en_US",
      title,
      description: opts.description,
      images: opts.ogImage ? [{ url: opts.ogImage }] : undefined,
    },
    other: opts.published ? { "article:published_time": opts.published } : undefined,
  };
}

export function orgJsonLd(site: SiteSettings, socials: Social[], lang: Lang, bookLabel: string) {
  const org: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "HealthAndBeautyBusiness",
    name: SITE_NAME,
    url: SITE_ORIGIN + "/",
    telephone: site.phone,
    email: site.email,
    address: `${site.address}, ${site.city}`,
    sameAs: socials.map((s) => s.url),
  };
  if (site.booking_url) {
    org.potentialAction = {
      "@type": "ReserveAction",
      name: bookLabel,
      target: {
        "@type": "EntryPoint",
        urlTemplate: site.booking_url,
        actionPlatform: ["http://schema.org/DesktopWebPlatform", "http://schema.org/MobileWebPlatform"],
      },
    };
  }
  return org;
}

export function serviceJsonLd(
  lang: Lang,
  svc: Service,
  site: SiteSettings,
  canonical: string,
  home: string,
  services: string,
  nav: string[],
) {
  const image = svc.image?.startsWith("http") ? svc.image : "";
  return {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Service",
        "@id": abs(canonical) + "#service",
        name: svc.title,
        serviceType: svc.title,
        description: svc.meta_description || svc.description.join(" "),
        url: abs(canonical),
        inLanguage: lang,
        ...(image ? { image } : {}),
        areaServed: { "@type": "City", name: "Budapest" },
        provider: {
          "@type": "HealthAndBeautyBusiness",
          name: SITE_NAME,
          url: SITE_ORIGIN + "/",
          telephone: site.phone,
          address: `${site.address}, ${site.city}`,
        },
      },
      {
        "@type": "BreadcrumbList",
        itemListElement: [
          { "@type": "ListItem", position: 1, name: nav[0], item: abs(home) },
          { "@type": "ListItem", position: 2, name: nav[1], item: abs(services) },
          { "@type": "ListItem", position: 3, name: svc.title, item: abs(canonical) },
        ],
      },
    ],
  };
}

export function blogJsonLd(
  post: { title: string; excerpt: string; iso_date: string; cover?: string },
  lang: Lang,
  socials: Social[],
  ogImage: string,
) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: post.title,
    description: post.excerpt,
    datePublished: post.iso_date,
    image: ogImage,
    inLanguage: lang,
    publisher: { "@type": "Organization", name: SITE_NAME, sameAs: socials.map((s) => s.url) },
  };
}

export function toLd(data: unknown) {
  return JSON.stringify(data).replace(/</g, "\\u003c");
}
