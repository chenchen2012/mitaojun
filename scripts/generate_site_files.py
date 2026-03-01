#!/usr/bin/env python3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
BASE = 'https://mitaojun.com'

EXCLUDE = {'post-template.html', 'post-minimal.html', 'contact-success.html'}

html_files = []
for p in sorted(ROOT.glob('*.html')):
    if p.name in EXCLUDE:
        continue
    html_files.append(p)

# sitemap.xml
lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
for p in html_files:
    if p.name == 'index.html':
        url = f'{BASE}/'
    else:
        url = f'{BASE}/{p.name}'
    lines.append('  <url>')
    lines.append(f'    <loc>{url}</loc>')
    lines.append(f'    <lastmod>{now}</lastmod>')
    lines.append('  </url>')
lines.append('</urlset>')
(ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')

# robots.txt
robots = [
    'User-agent: *',
    'Allow: /',
    '',
    'Disallow: /admin/',
    'Disallow: /include/',
    '',
    f'Sitemap: {BASE}/sitemap.xml',
]
(ROOT / 'robots.txt').write_text('\n'.join(robots) + '\n', encoding='utf-8')

# llms.txt
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

print(f'Generated sitemap.xml ({len(html_files)} urls), robots.txt, llms.txt')
