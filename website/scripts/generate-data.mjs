// Parses ../README.md (the awesome list) into src/data/projects.json.
// Run automatically before build so the site always mirrors the list.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const readme = readFileSync(join(here, "..", "..", "README.md"), "utf8");

const CATEGORIES = [
  "AI coworkers and teammates",
  "Agent builders and frameworks",
  "Workflow automation platforms",
  "Browser agents",
  "Coding agents",
];

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

writeFileSync(join(here, "..", "src", "data", "projects.json"), JSON.stringify(data, null, 2));
console.log(`generated projects.json: ${data.map((c) => `${c.name}=${c.projects.length}`).join(", ")}`);
