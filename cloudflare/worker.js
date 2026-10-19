// Cloudflare Worker: serves the exported static site (EN + HU) and implements POST /api/contact
// with the same JSON contract as the Django endpoint (backend/contact/views.py).
// Storage: D1 (binding DB, table from cloudflare/schema.sql) if bound, otherwise Workers KV (binding MESSAGES).

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const PHONE_RE = /^[+0-9 ()/.-]{5,40}$/;
const RATE_LIMIT = 5, RATE_WINDOW = 900; // 5 submissions / 15 min / IP

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra } });
}

function cors(request, env) {
  const origin = request.headers.get('origin');
  const allowed = (env.CORS_ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
  return origin && allowed.includes(origin)
    ? { 'access-control-allow-origin': origin, 'vary': 'Origin', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type' }
    : {};
}

async function rateLimited(env, ip) {
  if (!env.MESSAGES) return false; // KV used as a coarse counter
  const key = `rl:${ip}`;
  const n = parseInt((await env.MESSAGES.get(key)) || '0', 10) + 1;
  await env.MESSAGES.put(key, String(n), { expirationTtl: RATE_WINDOW });
  return n > RATE_LIMIT;
}

async function store(env, msg) {
  if (env.DB) {
    const r = await env.DB.prepare(
      'INSERT INTO contact_messages (name,email,phone,message,language,created_at,is_read,ip_address) VALUES (?,?,?,?,?,?,0,?)'
    ).bind(msg.name, msg.email, msg.phone, msg.message, msg.language, msg.created_at, msg.ip_address).run();
    return r.meta.last_row_id;
  }
  const id = `${msg.created_at}-${crypto.randomUUID().slice(0, 8)}`;
  await env.MESSAGES.put(`msg:${id}`, JSON.stringify({ id, ...msg, is_read: false }));
  return id;
}

async function contact(request, env) {
  const h = cors(request, env);
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: h });
  if (request.method !== 'POST') return json({ ok: false, error: 'method_not_allowed' }, 405, { allow: 'POST', ...h });
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  if (await rateLimited(env, ip)) return json({ ok: false, error: 'rate_limited' }, 429, h);

  let data;
  try {
    const ct = request.headers.get('content-type') || '';
    data = ct.includes('json') ? await request.json() : Object.fromEntries(await request.formData());
    if (!data || typeof data !== 'object' || Array.isArray(data)) throw 0;
  } catch { return json({ ok: false, error: 'invalid_json' }, 400, h); }

  const s = (k, n) => (typeof data[k] === 'string' ? data[k].trim().slice(0, n) : '');
  if (s('website', 200)) return json({ ok: true }, 201, h); // honeypot: pretend success, store nothing

  const lang = s('lang', 2);
  const msg = { name: s('name', 100), email: s('email', 200), phone: s('phone', 40), message: s('message', 5000),
    language: ['en', 'hu'].includes(lang) ? lang : 'en', created_at: new Date().toISOString(), ip_address: ip };
  const errors = {};
  if (msg.name.length < 2) errors.name = 'required';
  if (!EMAIL_RE.test(msg.email)) errors.email = 'invalid';
  if (msg.message.length < 5) errors.message = 'too_short';
  if (msg.phone && !PHONE_RE.test(msg.phone)) errors.phone = 'invalid';
  if (Object.keys(errors).length) return json({ ok: false, errors }, 422, h);

  const id = await store(env, msg);
  return json({ ok: true, id }, 201, h);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/contact' || url.pathname === '/api/contact/') return contact(request, env);
    if (url.pathname.startsWith('/api/')) return json({ ok: false, error: 'not_found' }, 404);
    return env.ASSETS.fetch(request); // static EN/HU site
  },
};
