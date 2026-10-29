import type { Metadata } from "next";
import { BlogIndexView } from "@/components/views";
import { blogMeta, loadBlog, revalidate as rev } from "@/lib/load";

export const revalidate = rev;

export function generateMetadata(): Metadata {
  return blogMeta("hu");
}

export default async function Page() {
  const data = await loadBlog("hu");
  return <BlogIndexView {...data} />;
}
