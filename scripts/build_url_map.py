#!/usr/bin/env python3
import csv
import re
import urllib.request
from pathlib import Path

SITEMAP_URL = 'https://mitaojun.com/sitemap.xml'
OUT = Path('/Users/cc801/Documents/mitaojun-github-archive/url-map.csv')

req = urllib.request.Request(
    SITEMAP_URL,
    headers={'User-Agent': 'Mozilla/5.0 (compatible; mitaojun-migrator/1.0)'}
)
xml = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
urls = re.findall(r'<loc>([^<]+)</loc>', xml)

with OUT.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['old_url', 'new_url', 'redirect_needed'])
    for u in urls:
        # keep URLs unchanged for best SEO
        w.writerow([u, u, 'no'])

print(f'Wrote {OUT} with {len(urls)} rows')
