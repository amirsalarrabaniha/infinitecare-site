import { bindings, defineConfig, defineWorker } from "cf/config";
import { createWorkersCacheConfig } from "@vinext/cloudflare/cache/config";

const cache = await createWorkersCacheConfig();

export default defineConfig({
  accountId: "164584608fafa1395f843df7bb17e1c7",
  worker: defineWorker({
    ...cache,
    name: "infinitecare-next",
    entrypoint: "vinext/server/fetch-handler",
    compatibilityDate: "2026-10-29",
    compatibilityFlags: ["nodejs_compat", "global_fetch_strictly_public"],
    observability: {
      enabled: true,
      traces: { enabled: true },
    },
    assets: {
      htmlHandling: "none",
      notFoundHandling: "none",
      runWorkerFirst: ["/*", "!/_next/static/*", "!/*/_next/static/*"],
    },
    env: {
      ...cache.env,
      ASSETS: bindings.assets(),
      VINEXT_KV_CACHE: bindings.kv(),
    },
  }),
});
