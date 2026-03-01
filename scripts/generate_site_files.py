#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path
import re

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
BASE = 'https://mitaojun.com'

EXCLUDE_FILES = {'post-template.html'}
EXCLUDE_DIRS = {'.git', 'raw-mirror'}


def iter_html_files():
    for p in sorted(ROOT.rglob('*.html')):
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.name in EXCLUDE_FILES:
            continue
        yield p


def extract_meta(text, pattern):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def is_noindex(text):
    m = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']', text, re.IGNORECASE)
    if not m:
        return False
    return 'noindex' in m.group(1).lower()


urls = {}
for p in iter_html_files():
    text = p.read_text(encoding='utf-8', errors='ignore')
    if is_noindex(text):
        continue
    canonical = extract_meta(text, r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']')
    if not canonical:
        # Fallback keeps sitemap resilient even if one page misses canonical.
        rel = p.relative_to(ROOT).as_posix()
        canonical = f'{BASE}/{rel}'
    if canonical not in urls:
        lastmod = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat()
        urls[canonical] = lastmod

lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in sorted(urls):
    lines.append('  <url>')
    lines.append(f'    <loc>{url}</loc>')
    lines.append(f'    <lastmod>{urls[url]}</lastmod>')
    lines.append('  </url>')
lines.append('</urlset>')
xml = '\n'.join(lines) + '\n'
(ROOT / 'sitemap.xml').write_text(xml, encoding='utf-8')
(ROOT / 'sitemap-full.xml').write_text(xml, encoding='utf-8')

robots = [
    'User-agent: *',
    'Allow: /',
    '',
    'Disallow: /admin/',
    'Disallow: /include/',
    'Disallow: /raw-mirror/',
    'Disallow: /post-template.html',
    '',
    f'Sitemap: {BASE}/sitemap.xml',
    f'Sitemap: {BASE}/sitemap-full.xml',
]
(ROOT / 'robots.txt').write_text('\n'.join(robots) + '\n', encoding='utf-8')

llms = [
    '# llms.txt',
    '',
    'Site: 蜜桃君成长记 (mitaojun.com)',
    'Purpose: 个人博客存档站点',
    '',
    '## Allowed',
    '- 允许搜索引擎索引公开页面',
    '- 允许展示标题、链接与简短摘要',
    '',
    '## Disallowed',
    '- 不允许将本站全文用于模型训练',
    '- 不允许未经授权的大规模再分发',
    '',
    '## Contact',
    '- 联系作者: https://mitaojun.com/contact.html',
]
(ROOT / 'llms.txt').write_text('\n'.join(llms) + '\n', encoding='utf-8')

print(f'Generated sitemap.xml/sitemap-full.xml ({len(urls)} canonical urls), robots.txt, llms.txt')
