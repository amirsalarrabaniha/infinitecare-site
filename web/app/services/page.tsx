import type { Metadata } from "next";
import { ServicesView } from "@/components/views";
import { loadServices, revalidate as rev, servicesMeta } from "@/lib/load";
import { UI } from "@/lib/ui";

export const revalidate = rev;

export async function generateMetadata(): Promise<Metadata> {
  const data = await loadServices("en");
  return servicesMeta("en", `${UI.en.desc} ${data.site.address}`);
}

export default async function Page() {
  const data = await loadServices("en");
  return <ServicesView {...data} />;
}
