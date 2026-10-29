import type { Metadata } from "next";
import { HomeView } from "@/components/views";
import { loadHome, revalidate as rev } from "@/lib/load";
import { toLd } from "@/lib/seo";
import { UI } from "@/lib/ui";

export const revalidate = rev;

export async function generateMetadata(): Promise<Metadata> {
  const data = await loadHome("en");
  return {
    title: `${UI.en.titles.index} | Infinite Care Beauty Clinic`,
    description: `${UI.en.desc} ${data.site.address}`,
    alternates: {
      canonical: "https://www.infinitecare.hu/",
      languages: {
        en: "https://www.infinitecare.hu/",
        hu: "https://www.infinitecare.hu/hu/",
        "x-default": "https://www.infinitecare.hu/",
      },
    },
    openGraph: {
      type: "website",
      url: "https://www.infinitecare.hu/",
      siteName: "Infinite Care Beauty Clinic",
      locale: "en_US",
      title: `${UI.en.titles.index} | Infinite Care Beauty Clinic`,
      description: `${UI.en.desc} ${data.site.address}`,
    },
  };
}

export default async function Page() {
  const data = await loadHome("en");
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: toLd(data.ld) }} />
      <HomeView {...data} />
    </>
  );
}
