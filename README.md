# mitaojun-github-archive

Static migration workspace for mitaojun.com.

## Goal

- Preserve original URL structure for best SEO.
- Keep content authored by you only.
- Migrate to static hosting (GitHub Pages compatible).

## Current local pages

- `index.html`
- `decision-making.html` (new styled article page)
- `contact.html`
- `contact-success.html`

## Generated SEO files

- `sitemap.xml` (current local published pages)
- `sitemap-full.xml` (full 234-url target sitemap from old site map)
- `robots.txt`
- `llms.txt`
- `url-map.csv` (old/new URL mapping, used for 301 planning)

## Scripts

- `scripts/snapshot_by_sitemap.py`
  - Downloads pages from the live sitemap and keeps original paths under `raw-mirror/`.
- `scripts/build_url_map.py`
  - Builds `url-map.csv` from live sitemap (`old_url == new_url` by default).
- `scripts/build_search_index.py`
  - Builds `assets/js/search-index.js` from local pages + mirrored archive pages.
- `scripts/generate_site_files.py`
  - Generates `sitemap.xml`, `robots.txt`, `llms.txt` for local published pages.
- `scripts/generate_full_sitemap_from_map.py`
  - Generates `sitemap-full.xml` from `url-map.csv`.
- `scripts/submit_baidu_urls.sh`
  - Submits URLs from a sitemap to Baidu's URL submission API.
  - Example: `scripts/submit_baidu_urls.sh --token <BAIDU_TOKEN> --site mitaojun.com --sitemap sitemap-full.xml --batch-size 20`

## Notes

- Keep article permalinks unchanged whenever possible.
- If any URL must change, use 301 permanent redirect.
- Homepage single source: edit `index.html` only. `index-worldclass-v2.html` is a redirect shim to avoid duplicate maintenance.
