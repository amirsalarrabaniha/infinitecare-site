import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ServiceLandingView } from "@/components/views";
import { allServiceSlugs } from "@/lib/api";
import { SITE_NAME } from "@/lib/config";
import { loadService, revalidate as rev } from "@/lib/load";
import { toLd } from "@/lib/seo";
import { abs } from "@/lib/urls";

export const revalidate = rev;
export const dynamicParams = true;

const RESERVED = new Set([
  "api",
  "hu",
  "en",
  "blog",
  "services",
  "sitemap.xml",
  "robots.txt",
  "llms.txt",
  "assets",
  "css",
  "js",
]);

export async function generateStaticParams() {
  const slugs = await allServiceSlugs();
  return slugs.map((s) => ({ slug: s.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  if (RESERVED.has(slug)) return {};
  const data = await loadService(slug);
  if (!data) return { robots: { index: false } };
  const title = `${data.svc.meta_title || data.svc.title} | ${SITE_NAME}`;
  const description = data.svc.meta_description || data.ui.desc;
  return {
    title,
    description,
    alternates: {
      canonical: abs(data.canonical),
      languages: {
        en: abs(data.switchUrls.en),
        hu: abs(data.switchUrls.hu),
        "x-default": abs(data.switchUrls.en),
      },
    },
    openGraph: {
      type: "website",
      url: abs(data.canonical),
      siteName: SITE_NAME,
      locale: data.lang === "hu" ? "hu_HU" : "en_US",
      title,
      description,
      images: data.svc.image ? [{ url: data.svc.image }] : undefined,
    },
  };
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  if (RESERVED.has(slug)) notFound();
  const data = await loadService(slug);
  if (!data) notFound();
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: toLd(data.ld) }} />
      <ServiceLandingView {...data} />
    </>
  );
}
