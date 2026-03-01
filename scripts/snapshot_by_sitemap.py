#!/usr/bin/env python3
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

SITEMAP_URL = 'https://mitaojun.com/sitemap.xml'
ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive/raw-mirror')
ROOT.mkdir(parents=True, exist_ok=True)

def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (compatible; mitaojun-migrator/1.0)'}
    )
    return urllib.request.urlopen(req, timeout=30).read()

xml = fetch_bytes(SITEMAP_URL).decode('utf-8', errors='ignore')
urls = re.findall(r'<loc>([^<]+)</loc>', xml)

count = 0
for u in urls:
    p = urlparse(u)
    path = p.path
    if not path or path == '/':
        local = ROOT / 'index.html'
    else:
        rel = path.lstrip('/')
        if rel.endswith('/'):
            local = ROOT / rel / 'index.html'
        else:
            local = ROOT / rel
    local.parent.mkdir(parents=True, exist_ok=True)
    try:
        html = fetch_bytes(u)
        local.write_bytes(html)
        count += 1
    except Exception as e:
        print(f'FAILED {u}: {e}')

print(f'Downloaded {count}/{len(urls)} urls into {ROOT}')
