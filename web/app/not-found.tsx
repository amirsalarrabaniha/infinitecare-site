import { loadChrome } from "@/lib/load";
import { SiteShell } from "@/components/chrome";

export default async function NotFound() {
  const { site, socials, ui } = await loadChrome("en");
  return (
    <SiteShell lang="en" navKey="index" site={site} socials={socials} ui={ui} switchUrls={{ en: "/", hu: "/hu/" }}>
      <main className="post">
        <article className="wrap post-in" style={{ paddingTop: "8rem", paddingBottom: "6rem" }}>
          <h1>Page not found</h1>
          <p>This page is not available. Please return to the home page or our treatments.</p>
          <p>
            <a className="btn" href="/">
              Home
            </a>
          </p>
        </article>
      </main>
    </SiteShell>
  );
}
