// Parses ../README.md (the awesome list) into src/data/projects.json and
// copies the market map into public/. Run automatically before dev/build so
// the site always mirrors the list. Creates its target directories because
// they only hold generated (gitignored) files and are absent in a fresh clone.
import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const readme = readFileSync(join(root, "..", "README.md"), "utf8");

const CATEGORIES = [
  "AI coworkers and teammates",
  "Agent builders and frameworks",
  "Workflow automation platforms",
  "Browser agents",
  "Coding agents",
];

// Canonical category slugs, kept in sync with src/pages/categories/[slug].astro.
const CATEGORY_SLUGS = {
  "AI coworkers and teammates": "ai-coworkers",
  "Agent builders and frameworks": "agent-builders",
  "Workflow automation platforms": "workflow-automation",
  "Browser agents": "browser-agents",
  "Coding agents": "coding-agents",
};

const data = [];
let current = null;
for (const line of readme.split("\n")) {
  const h = line.match(/^## (.+)$/);
  if (h) {
    current = CATEGORIES.includes(h[1].trim())
      ? { name: h[1].trim(), description: "", projects: [] }
      : null;
    if (current) data.push(current);
    continue;
  }
  if (!current) continue;
  const e = line.match(
    /^- \[([^\]]+)\]\((https:\/\/github\.com\/([^/)]+)[^)]*)\) - (.+?) License: (.+?)\. Hosting: (.+?)\.?$/
  );
  if (e) {
    current.projects.push({
      name: e[1],
      repo: e[2],
      org: e[3],
      description: e[4].trim(),
      license: e[5].trim(),
      hosting: e[6].trim(),
    });
  } else if (line.trim() && !line.startsWith("-") && current.projects.length === 0 && !current.description) {
    current.description = line.trim();
  }
}

mkdirSync(join(root, "src", "data"), { recursive: true });
writeFileSync(join(root, "src", "data", "projects.json"), JSON.stringify(data, null, 2));
console.log(`generated projects.json: ${data.map((c) => `${c.name}=${c.projects.length}`).join(", ")}`);

mkdirSync(join(root, "public"), { recursive: true });
const map = join(root, "..", "media", "market-map.svg");
if (existsSync(map)) {
  copyFileSync(map, join(root, "public", "market-map.svg"));
  console.log("copied market-map.svg");
} else {
  console.warn("WARN media/market-map.svg missing; run scripts/market_map.py first");
}

// Social preview doubles as the Open Graph image.
const banner = join(root, "..", "media", "social-preview.png");
if (existsSync(banner)) {
  copyFileSync(banner, join(root, "public", "og.png"));
  console.log("copied og.png");
} else {
  console.warn("WARN media/social-preview.png missing; og:image will 404 until CI renders it");
}

// Sitemap with lastmod, covering every static route.
const lastmod = (process.env.BUILD_DATE || new Date().toISOString().slice(0, 10));
const detailsPath = join(root, "src", "data", "platform-details.json");
const slugs = existsSync(detailsPath)
  ? JSON.parse(readFileSync(detailsPath, "utf8")).map((p) => p.slug)
  : [];
const catRoutes = Object.values(CATEGORY_SLUGS).map((s) => `/categories/${s}/`);
const urls = [
  "/",
  "/faq/",
  "/how-to-choose/",
  "/updates/",
  "/platforms/",
  ...catRoutes,
  ...slugs.map((s) => `/platforms/${s}/`),
];
const sitemap = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
  ...urls.map(
    (u) => `  <url><loc>https://aiagentplatforms.dev${u}</loc><lastmod>${lastmod}</lastmod></url>`
  ),
  "</urlset>",
  "",
].join("\n");
writeFileSync(join(root, "public", "sitemap.xml"), sitemap);
console.log(`sitemap.xml: ${urls.length} urls, lastmod ${lastmod}`);
