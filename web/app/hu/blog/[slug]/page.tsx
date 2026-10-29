import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { BlogPostView } from "@/components/views";
import { getBlog } from "@/lib/api";
import { loadPost, postMeta, revalidate as rev } from "@/lib/load";
import { toLd } from "@/lib/seo";

export const revalidate = rev;
export const dynamicParams = true;

export async function generateStaticParams() {
  const posts = await getBlog("hu");
  return posts.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const data = await loadPost("hu", slug);
  if (!data) return { title: "Blog | Infinite Care Beauty Clinic", robots: { index: false } };
  return postMeta("hu", data.post);
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const data = await loadPost("hu", slug);
  if (!data) notFound();
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: toLd(data.ld) }} />
      <BlogPostView {...data} />
    </>
  );
}
