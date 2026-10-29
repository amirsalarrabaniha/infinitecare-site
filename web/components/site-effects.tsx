"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    initInfiniteCare?: () => void;
  }
}

/** Re-run vanilla site.js after React hydration so IntersectionObserver sees live nodes. */
export function SiteEffects() {
  useEffect(() => {
    const run = () => window.initInfiniteCare?.();
    run();
    const a = requestAnimationFrame(() => {
      run();
      requestAnimationFrame(run);
    });
    const t = window.setTimeout(run, 80);
    return () => {
      cancelAnimationFrame(a);
      window.clearTimeout(t);
    };
  }, []);
  return null;
}
