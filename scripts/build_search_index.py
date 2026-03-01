#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
RAW = ROOT / 'raw-mirror'
OUT = ROOT / 'assets/js/search-index.js'
BASE = 'https://mitaojun.com'

EXCLUDE = {'post-template.html', 'post-minimal.html', 'contact-success.html', 'contact.html', 'index.html', 'archive.html'}


def strip_tags(s: str) -> str:
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def get_title(html: str, fallback: str) -> str:
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.S)
    if m:
        return strip_tags(m.group(1))
    m = re.search(r'<title>(.*?)</title>', html, re.I | re.S)
    if m:
        t = strip_tags(m.group(1))
        return t.split('|')[0].strip()
    return fallback


def get_date_category(html: str):
    m = re.search(r'<p class="post-kicker">(.*?)</p>', html, re.I | re.S)
    if not m:
        return '', ''
    text = strip_tags(m.group(1))
    parts = [x.strip() for x in text.split('/')]
    if len(parts) >= 2:
        return parts[1], parts[0]
    return '', ''


def get_snippet(html: str) -> str:
    m = re.search(r'<article[^>]*class="post-article"[^>]*>(.*?)</article>', html, re.I | re.S)
    block = m.group(1) if m else html
    pm = re.search(r'<p(?![^>]*copyright-note)[^>]*>(.*?)</p>', block, re.I | re.S)
    if not pm:
        return ''
    txt = strip_tags(pm.group(1))
    return txt[:140]


entries = {}

# local styled pages (high priority)
for path in sorted(ROOT.glob('*.html')):
    if path.name in EXCLUDE:
        continue
    html = path.read_text(encoding='utf-8', errors='ignore')
    title = get_title(html, path.stem)
    date, cat = get_date_category(html)
    snippet = get_snippet(html)
    url = f'{BASE}/{path.name}'
    entries[url] = {
        'title': title,
        'url': url,
        'category': cat,
        'date': date,
        'text': snippet,
    }

# raw mirror pages (full archive coverage)
if RAW.exists():
    for path in sorted(p for p in RAW.rglob('*') if p.is_file()):
        rel = path.relative_to(RAW).as_posix()
        if rel == 'index.html':
            url = f'{BASE}/'
        else:
            url = f'{BASE}/{rel}'
        if url in entries:
            continue
        html = path.read_text(encoding='utf-8', errors='ignore')
        if '<html' not in html.lower():
            continue
        title = get_title(html, Path(rel).stem)
        # raw pages usually contain full datetime in <time datetime="...">
        dm = re.search(r'<time[^>]*datetime=\"(\\d{4}-\\d{2}-\\d{2})', html, re.I)
        date = dm.group(1) if dm else ''
        snippet = get_snippet(html)
        entries[url] = {
            'title': title,
            'url': url,
            'category': '',
            'date': date,
            'text': snippet,
        }
values = sorted(entries.values(), key=lambda x: x['url'])
OUT.write_text(
    'window.MITAOJUN_SEARCH_INDEX = ' + json.dumps(values, ensure_ascii=False, indent=2) + ';\n',
    encoding='utf-8',
)
print(f'Wrote {OUT} with {len(values)} entries')
