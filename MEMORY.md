# mitaojun.com Memory File

This file records key long-term decisions and maintenance knowledge for creating and operating `mitaojun.com`.

## 1) Project Identity
- Site name: `蜜桃君成长记`
- Domain: `https://mitaojun.com`
- Hosting: GitHub Pages (repo-driven static site)
- Content focus: archived Chinese text articles from earlier blog era, with modernized layout/SEO.

## 2) Core Experience Decisions
- Keep a unified background tone across pages (no separate white cards behind article body/sidebar content).
- Article page uses a two-column desktop layout (content + right sidebar), with generous spacing to reduce visual pressure.
- Sidebar should be clean, no excessive boxed widgets.
- Category names in UI omit old prefix labels (e.g., hide “爱情：”), while SEO/source text can keep original semantics.
- About image in sidebar: use site-hosted image asset, shown at reduced size.
- Footer style should be consistent across all pages.

## 3) Homepage / Archive / Record Strategy
- Homepage and archive/record pages should have related visual language but not identical interaction intent.
- Archive naming: use “存档” (not “归档”).
- Monthly archive list should show real counts as `（文章数）`.
- `/record/` is the month index; `/record/YYYYMM` pages are monthly detail pages.

## 4) Search UX (Important)
- Search now follows **submit-and-navigate** model:
  - Sidebar form submits to `/search.html?q=关键词`.
  - Do not rely on inline “type and wait under input” for primary UX.
- Search result page:
  - `search.html`
  - shows immediate loading state (`正在搜索…`) before index resolves.
- JS behavior:
  - `assets/js/site.js` sets search form `action=/search.html`, `method=get`, input `name=q`.
  - Full index source: `assets/js/search-index.js`.

## 5) SEO / Analytics / Verification
- Standard page head should include:
  - canonical
  - Open Graph + Twitter cards
  - JSON-LD (when applicable)
  - `meta robots` appropriate to page type
- Verification tokens in use:
  - Google: `unToYoFWQqV-eI3dsZkiNMGIUO8IFP6PSWyx5TGHLWc`
  - Baidu: `dDODIHx5iul9rQRx`
- Analytics scripts in use:
  - GA4 Measurement ID: `G-0L9V2H3H6J`
  - Baidu HM token: `71e78e372cab1881685ab00b38154843`

## 6) Typography & Rendering for Chinese Users
- Prioritize Chinese readability on mainland user systems.
- Font stack in CSS is tuned for Chinese serif fallback across macOS/iOS/Windows/Android.
- Do not force a single exact cross-platform font; prioritize graceful fallback quality.

## 7) Article Content Standards
- Keep original text meaning; normalize structure only.
- Prefer semantic structure:
  - `<h2>` for section headings
  - `<p>` for paragraphs
  - `<ol><li>` for numbered points (not fake numbering inside `<p>`)
- Ordered list alignment was standardized globally in CSS/JS to avoid “number floating upward”.

## 8) Known Historical Cleanup Decisions
- `post-158.html` was removed completely.
- Related month page `record/200506/index.html` was removed.
- References were cleaned from:
  - navigation links
  - record index
  - sitemap files
  - search index
  - url map

## 9) Critical Files to Know
- Main stylesheet: `assets/css/main.css`
- Main site script: `assets/js/site.js`
- Search index data: `assets/js/search-index.js`
- Main pages: `index.html`, `archive.html`, `search.html`, `404.html`
- Month index: `record/index.html`
- Sitemap: `sitemap.xml`, `sitemap-full.xml`

## 10) Maintenance Workflow (Recommended)
1. Edit locally.
2. Check references globally (`rg`) for removed/renamed URLs.
3. Validate key UX flows:
   - article page layout
   - search submit -> search page result
   - archive/record navigation
   - 404 page behavior
4. Validate sitemap consistency when adding/removing pages.
5. Commit with clear message and push to `main`.
6. Hard refresh after deploy due to asset caching.

## 11) Guardrails
- Avoid reintroducing heavy widget boxes/background cards unless explicitly requested.
- Do not add large headline elements that visually overpower the blog title.
- Keep desktop-first refinement when requested; then adapt mobile.
- Preserve SEO/meta/analytics consistency on all newly created pages.
