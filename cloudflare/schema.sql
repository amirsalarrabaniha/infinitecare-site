-- D1 schema (same fields as Django's ContactMessage). Apply: npx wrangler d1 execute infinitecare-messages --remote --file cloudflare/schema.sql
CREATE TABLE IF NOT EXISTS contact_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT DEFAULT '', message TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'en', created_at TEXT NOT NULL, is_read INTEGER NOT NULL DEFAULT 0, ip_address TEXT
);
CREATE INDEX IF NOT EXISTS idx_contact_created ON contact_messages(created_at);
