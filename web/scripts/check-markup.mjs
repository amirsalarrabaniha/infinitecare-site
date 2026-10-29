/** Parity checks against backend/content/tests.py BodyMarkupTests. */
function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}
function linkify(text) {
  const src = String(text ?? "");
  const re = /\[([^\]\n]{1,200})\]\(((?:https?:\/\/|\/)[^\s()<>"]*)\)|(https?:\/\/[^\s<>"]+[^\s<>".,;:!?)])/g;
  let out = "", pos = 0, m;
  while ((m = re.exec(src))) {
    out += escapeHtml(src.slice(pos, m.index));
    const label = m[2] ? m[1] : m[3], url = m[2] || m[3];
    const external = /^http/.test(url) && !url.startsWith("https://www.infinitecare.hu");
    out += `<a href="${escapeHtml(url)}"${external ? ' target="_blank" rel="noopener"' : ""}>${escapeHtml(label)}</a>`;
    pos = m.index + m[0].length;
  }
  return out + escapeHtml(src.slice(pos));
}
function faqMark(blocks) {
  let faq = false;
  return (blocks || []).map((b) => {
    if (b.type !== "h") return b;
    const t = String(b.text || "").replace(/\s+$/, "");
    if (/^\s*(frequently asked questions|gyakran ism[eé]telt k[eé]rd[eé]sek|faq)\b/i.test(t)) {
      faq = true;
      return b;
    }
    if (faq && t.endsWith("?")) return { type: "q", text: b.text };
    faq = false;
    return b;
  });
}

const out = linkify("See [cellulite therapy](/cellulite-therapy) or book at https://l.fresha.com/x. <b>&");
const checks = [
  [out.includes('<a href="/cellulite-therapy">cellulite therapy</a>'), "internal markdown link"],
  [out.includes('<a href="https://l.fresha.com/x" target="_blank" rel="noopener">https://l.fresha.com/x</a>.'), "autolink + trailing period"],
  [out.includes("&lt;b&gt;&amp;"), "escaped HTML"],
  [!linkify("[x](javascript:alert(1))").includes('<a href="javascript'), "javascript rejected"],
  [linkify("[x](javascript:alert(1))") === "[x](javascript:alert(1))", "javascript left as text"],
  [linkify('[a"><script>](https://www.infinitecare.hu/a)') === '<a href="https://www.infinitecare.hu/a">a&quot;&gt;&lt;script&gt;</a>', "internal site no new tab + escaped label"],
];
const bl = [
  { type: "h", text: "What is it?" },
  { type: "h", text: "Frequently asked questions" },
  { type: "h", text: "Does it hurt?" },
  { type: "p", text: "No." },
  { type: "h", text: "Book a consultation" },
  { type: "h", text: "Later?" },
];
checks.push([["h", "h", "q", "p", "h", "h"].join() === faqMark(bl).map((b) => b.type).join(), "faq mark EN"]);
checks.push([faqMark([{ type: "h", text: "Gyakran ismételt kérdések" }, { type: "h", text: "Fáj?" }])[1].type === "q", "faq mark HU"]);
const failed = checks.filter(([ok]) => !ok);
if (failed.length) {
  console.error("check-markup failed:", failed.map(([, n]) => n));
  process.exit(1);
}
console.log(`check-markup: ${checks.length} ok`);
