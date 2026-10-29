import { getBlog, getServices } from "@/lib/api";
import { SITE_ORIGIN } from "@/lib/config";
import { pagePath, servicePath } from "@/lib/urls";

export const revalidate = 180;

export async function GET() {
  const [enServices, huServices, posts] = await Promise.all([
    getServices("en"),
    getServices("hu"),
    getBlog("en"),
  ]);
  const lines = [
    "# Infinite Care Beauty Clinic",
    "",
    "> Beauty and aesthetic clinic in Budapest (Bp. VI. Podmaniczky str. 5.). Treatments such as microneedling, laser hair removal, EMSCULPT and teeth whitening. The website is available in English and Hungarian.",
    "",
    "## Pages",
    "",
    `- [Home](${SITE_ORIGIN}/): clinic introduction, photo gallery, treatment videos and the contact form`,
    `- [Our treatments](${SITE_ORIGIN}${pagePath("en", "services")}): all treatments`,
    `- [Blog](${SITE_ORIGIN}${pagePath("en", "blog")}): articles about treatments and skin care`,
  ];
  for (const s of enServices) {
    if (!s.slug) continue;
    lines.push(`- [${s.title}](${SITE_ORIGIN}${servicePath(s.slug)}): ${s.meta_description || s.title}`);
  }
  for (const p of posts) {
    lines.push(`- [${p.title}](${SITE_ORIGIN}${pagePath("en", "blog", p.slug)})`);
  }
  lines.push("", "## Magyar", "");
  lines.push(`- [Főoldal](${SITE_ORIGIN}/hu/)`);
  lines.push(`- [Szolgáltatásaink](${SITE_ORIGIN}${pagePath("hu", "services")})`);
  lines.push(`- [Blog](${SITE_ORIGIN}${pagePath("hu", "blog")})`);
  for (const s of huServices) {
    if (!s.slug) continue;
    lines.push(`- [${s.title}](${SITE_ORIGIN}${servicePath(s.slug)})`);
  }
  lines.push(
    "",
    "## Contact",
    "",
    "- Phone: +36 1 707 0075",
    "- E-mail: info@infinitecare.hu",
    "- Address: Bp. VI. Podmaniczky str. 5., Budapest, Hungary",
  );
  return new Response(lines.join("\n") + "\n", {
    headers: { "content-type": "text/plain; charset=utf-8" },
  });
}
