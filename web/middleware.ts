import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const LEGACY: Record<string, string> = {
  "/home": "/",
  "/home/": "/",
  "/home.html": "/",
  "/fooldal": "/hu/",
  "/fooldal/": "/hu/",
  "/fooldal.html": "/hu/",
  "/szolgaltatasaink": "/hu/services",
  "/szolgaltatasaink/": "/hu/services",
  "/szolgaltatasaink.html": "/hu/services",
  "/araink": "/hu/services",
  "/araink/": "/hu/services",
  "/araink.html": "/hu/services",
  "/prices": "/services",
  "/prices/": "/services",
  "/prices.html": "/services",
  "/hu/prices": "/hu/services",
  "/hu/prices/": "/hu/services",
  "/hu/prices.html": "/hu/services",
};

const HU_SERVICE_SLUGS = new Set([
  "exoszoma-terapia",
  "lezeres-tartos-szortelenites",
  "mezoterapia",
  "ems-testkezeles",
  "cellulit-terapia",
  "carbon-hamlasztas",
  "fogfeherites",
  "face-lifting",
  "brazilift",
]);

function pageKind(pathname: string) {
  if (pathname === "/blog" || pathname === "/hu/blog") return "blog";
  if (pathname.startsWith("/blog/") || pathname.startsWith("/hu/blog/")) return "blog_post";
  if (pathname === "/services" || pathname === "/hu/services") return "services";
  if (pathname === "/" || pathname === "/hu" || pathname === "/hu/") return "index";
  return "service";
}

function langOf(pathname: string) {
  if (pathname === "/hu" || pathname === "/hu/" || pathname.startsWith("/hu/")) return "hu";
  const slug = pathname.replace(/^\//, "").replace(/\/$/, "");
  if (HU_SERVICE_SLUGS.has(slug)) return "hu";
  return "en";
}

function stripHtml(pathname: string) {
  if (!pathname.endsWith(".html")) return pathname;
  let dest = pathname.slice(0, -5);
  if (dest === "/index" || dest.endsWith("/index")) {
    dest = dest.slice(0, -5) || "/";
    if (dest === "/hu") dest = "/hu/";
  }
  return dest;
}

function securityHeaders(res: NextResponse) {
  res.headers.set("X-Content-Type-Options", "nosniff");
  res.headers.set("X-Frame-Options", "SAMEORIGIN");
  res.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  res.headers.set(
    "Permissions-Policy",
    "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()",
  );
  res.headers.set("Cross-Origin-Opener-Policy", "same-origin");
  res.headers.set(
    "Content-Security-Policy",
    "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://infinitecare-api.amyrsalarr.workers.dev; font-src 'self'; media-src 'self' https://infinitecare-api.amyrsalarr.workers.dev; connect-src 'self' https://infinitecare-api.amyrsalarr.workers.dev; frame-src https://www.google.com https://maps.google.com https://www.youtube-nocookie.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'; upgrade-insecure-requests",
  );
  return res;
}

export function middleware(request: NextRequest) {
  const url = request.nextUrl;
  const { pathname } = url;

  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/assets/") ||
    pathname.startsWith("/css/") ||
    pathname.startsWith("/js/")
  ) {
    return NextResponse.next();
  }

  if (pathname === "/blog/post" || pathname === "/hu/blog/post") {
    const p = url.searchParams.get("p");
    if (p) {
      const dest = pathname.startsWith("/hu") ? `/hu/blog/${encodeURIComponent(p)}` : `/blog/${encodeURIComponent(p)}`;
      return NextResponse.redirect(new URL(dest, url.origin), 301);
    }
  }

  const legacy = LEGACY[pathname] || (pathname.endsWith(".html") ? LEGACY[stripHtml(pathname)] : undefined);
  if (legacy) return NextResponse.redirect(new URL(legacy, url.origin), 301);

  if (pathname.endsWith(".html")) {
    return NextResponse.redirect(new URL(stripHtml(pathname) + url.search, url.origin), 301);
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-ic-lang", langOf(pathname));
  requestHeaders.set("x-ic-page", pageKind(pathname));
  const res = NextResponse.next({ request: { headers: requestHeaders } });
  res.headers.set("x-ic-lang", langOf(pathname));
  res.headers.set("x-ic-page", pageKind(pathname));
  return securityHeaders(res);
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
