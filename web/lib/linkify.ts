import type { BodyBlock } from "./types";

const ESC: Record<string, string> = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;",
};

export function escapeHtml(text: string) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => ESC[c] || c);
}

/** Escape, then turn [label](url) and bare http(s) URLs into links. Matches Django `linkify` / js/main.js. */
export function linkify(text: string) {
  const src = String(text ?? "");
  const re =
    /\[([^\]\n]{1,200})\]\(((?:https?:\/\/|\/)[^\s()<>"]*)\)|(https?:\/\/[^\s<>"]+[^\s<>".,;:!?)])/g;
  let out = "";
  let pos = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(src))) {
    out += escapeHtml(src.slice(pos, m.index));
    const label = m[2] ? m[1] : m[3];
    const url = m[2] || m[3];
    const external = /^http/.test(url) && !url.startsWith("https://www.infinitecare.hu");
    out += `<a href="${escapeHtml(url)}"${external ? ' target="_blank" rel="noopener"' : ""}>${escapeHtml(label)}</a>`;
    pos = m.index + m[0].length;
  }
  return out + escapeHtml(src.slice(pos));
}

const FAQ_RE = /^\s*(frequently asked questions|gyakran ism[eé]telt k[eé]rd[eé]sek|faq)\b/i;

/** Headings after an FAQ section title that end in '?' become smaller FAQ questions. */
export function faqMark(blocks: BodyBlock[] | null | undefined): BodyBlock[] {
  let faq = false;
  return (blocks || []).map((b) => {
    if (b.type !== "h") return b;
    const t = String(b.text || "").replace(/\s+$/, "");
    if (FAQ_RE.test(t)) {
      faq = true;
      return b;
    }
    if (faq && t.endsWith("?")) return { type: "q" as const, text: b.text };
    faq = false;
    return b;
  });
}

export function brk(text: string) {
  return escapeHtml(text).replace(/\r?\n/g, "<br>");
}
