#!/usr/bin/env python3
import csv
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
MAP = ROOT / 'url-map.csv'
OUT = ROOT / 'sitemap-full.xml'

rows = list(csv.DictReader(MAP.open(encoding='utf-8')))
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for r in rows:
    lines.append('  <url>')
    lines.append(f"    <loc>{r['new_url']}</loc>")
    lines.append(f'    <lastmod>{now}</lastmod>')
    lines.append('  </url>')
lines.append('</urlset>')
OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Wrote {OUT} with {len(rows)} urls')
