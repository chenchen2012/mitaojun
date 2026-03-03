# SEO Checklist (Google + Baidu) — mitaojun.com

Date: 2026-03-03

## 1) Sitemap Submission
- Google Search Console
  - Property: `https://mitaojun.com/`
  - Submit: `https://mitaojun.com/sitemap.xml`
- Baidu Zhanzhang
  - Site: `https://mitaojun.com/`
  - Submit: `https://mitaojun.com/sitemap.xml`

## 2) URL Inspection Priority (Top URLs)
- Homepage: `https://mitaojun.com/`
- Archive: `https://mitaojun.com/archive.html`
- Key posts:
  - `https://mitaojun.com/decision-making.html`
  - `https://mitaojun.com/junyi-tao.html`
  - `https://mitaojun.com/post-111.html`
  - `https://mitaojun.com/post-83.html`

## 3) Redirect Validation (SEO-critical)
- Old category URLs should return `301`:
  - `/sort/ad` and `/sort/ad/` -> `/sort/life/`
  - `/sort/internet` and `/sort/internet/` -> `/sort/life/`
  - `/sort/language` and `/sort/language/` -> `/sort/philosophy/`
- Check command:
```bash
curl -I https://mitaojun.com/sort/ad/
curl -I https://mitaojun.com/sort/internet/
curl -I https://mitaojun.com/sort/language/
```

## 4) Structured Data Validation
- Homepage:
  - `WebSite` + `SearchAction` present.
- Article pages:
  - `BlogPosting` present.
  - `BreadcrumbList` present.
- Validate with Google Rich Results Test and schema validator.

## 5) Indexing Hygiene
- Keep `search.html` as `noindex,follow`.
- Keep `404.html` as `noindex,follow`.
- Keep migrated placeholder pages canonicalized to target category and noindexed.

## 6) Weekly Monitoring (4 Weeks)
- Google Search Console:
  - Pages indexed trend
  - Crawl stats
  - Redirected URL bucket
  - Coverage errors (5xx, soft 404, duplicate without canonical)
- Baidu Zhanzhang:
  - 收录量变化
  - 抓取频次
  - 死链/异常页

## 7) Expected Timeline
- Technical changes recognized: usually within a few days.
- Indexing and snippet changes: usually 1-4 weeks.

