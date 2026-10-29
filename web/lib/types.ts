export type BodyBlock =
  | { type: "h" | "q"; text: string }
  | { type: "p"; text: string }
  | { type: "ul"; items: string[] };

export type SiteSettings = {
  phone: string;
  phone_href: string;
  email: string;
  address: string;
  hours: string[];
  tagline: string;
  city: string;
  facebook: string;
  instagram: string;
  youtube: string;
  tiktok: string;
  booking_url: string;
  offers_url: string;
  map_embed: string;
};

export type FeatureBlock = {
  image: string;
  eyebrow: string;
  title: string;
  paragraphs: string[];
  button: string;
};

export type HomeContent = {
  hero_image: string;
  hello: string;
  h1_main: string;
  h1_em: string;
  lead: string;
  marquee: string[];
  f1: FeatureBlock;
  f2: FeatureBlock;
  cta_image: string;
  cta_script: string;
  cta_title: string;
  cta_button: string;
  contact_eyebrow: string;
  contact_title: string;
  contact_text: string;
  contact_image: string;
  counters: { value: number; suffix: string; label: string }[];
};

export type YouTubeClip = {
  id: number;
  youtube_id: string;
  title: string;
  caption: string;
  poster: string;
  width: number;
  height: number;
  vertical: boolean;
  category: string;
  cats: string;
  featured: boolean;
  home: boolean;
  gallery: boolean;
  service_id: number | null;
  post_id: number | null;
};

export type GalleryPhoto = {
  id: number;
  image: string;
  category: string;
  cats: string;
  alt: string;
  width: number;
  height: number;
};

export type VideoClip = {
  id: number;
  video: string;
  poster: string;
  title: string;
  category: string;
};

export type GalleryPayload = {
  photos: GalleryPhoto[];
  videos: VideoClip[];
  youtube: YouTubeClip[];
};

export type Service = {
  videos: YouTubeClip[];
  id: number;
  image: string;
  eyebrow: string;
  title: string;
  description: string[];
  order: number;
  slug: string;
  slugs: { en: string; hu: string };
  meta_title: string;
  meta_description: string;
  blocks: BodyBlock[];
  gallery_category: string;
  updated: string;
  href?: string;
};

export type BlogSummary = {
  slug: string;
  title: string;
  excerpt: string;
  cover: string;
  date: string;
  iso_date: string;
  url: string;
};

export type BlogPost = BlogSummary & {
  blocks: BodyBlock[];
  videos: YouTubeClip[];
};

export type Social = {
  key: string;
  name: string;
  url: string;
  label: string;
};
