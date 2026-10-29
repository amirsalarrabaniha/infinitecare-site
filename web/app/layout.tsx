import type { Metadata } from "next";
import { headers } from "next/headers";
import { SiteEffects } from "@/components/site-effects";
import { API_CONTACT, SITE_NAME, SITE_ORIGIN, THEME_COLOR } from "@/lib/config";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_ORIGIN),
  title: { default: SITE_NAME, template: "%s" },
  icons: {
    icon: [
      { url: "/assets/images/favicon.ico" },
      { url: "/assets/images/infinitecare-96.png", sizes: "96x96", type: "image/png" },
    ],
  },
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const h = await headers();
  const lang = h.get("x-ic-lang") === "hu" ? "hu" : "en";
  const page = h.get("x-ic-page") || "index";
  const postTpl = lang === "hu" ? "/hu/blog/__SLUG__" : "/blog/__SLUG__";
  return (
    <html lang={lang}>
      <head>
        <meta name="theme-color" content={THEME_COLOR} />
        <link rel="preload" href="/assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/assets/fonts/playfair-display-latin.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="stylesheet" href="/css/style.css" />
      </head>
      <body className={`page-${page}`} data-lang={lang} data-api={API_CONTACT} data-post={postTpl} data-root="/">
        <div className="loader">
          <img src="/assets/images/infinitecare-logo-4.png" alt="" width={248} height={260} />
        </div>
        <div className="cursor-glow"></div>
        <div className="progress"></div>
        {children}
        <SiteEffects />
        <script src="/js/site.js" defer />
      </body>
    </html>
  );
}
