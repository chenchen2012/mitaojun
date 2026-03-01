#!/usr/bin/env python3
import re
from datetime import datetime
from pathlib import Path

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
RAW = ROOT / 'raw-mirror'
TEMPLATE_PATH = ROOT / 'post-template.html'

EXCLUDE_PAGES = {
    'index.html',
    'archive.html',
    'contact.html',
    'contact-success.html',
}

PUBLISHER_LOGO = 'https://mitaojun.com/content/uploadfile/202011/42081605882236.jpg'
AUTHOR = '蜜桃君'

ALLOWED = {
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'ul', 'ol', 'li', 'a', 'img', 'br',
    'strong', 'em', 'b', 'i', 'u'
}


def strip_tags(s: str) -> str:
    s = re.sub(r'(?is)<script[^>]*>.*?</script>', ' ', s)
    s = re.sub(r'(?is)<style[^>]*>.*?</style>', ' ', s)
    s = re.sub(r'(?is)<[^>]+>', ' ', s)
    s = s.replace('&nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def extract(raw: str, pat: str, default: str = '') -> str:
    m = re.search(pat, raw, re.I | re.S)
    return m.group(1).strip() if m else default


def clean_body(html: str) -> str:
    html = html.replace('\ufeff', '')
    html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
    html = re.sub(r'(?is)<style[^>]*>.*?</style>', '', html)
    html = re.sub(r'(?is)<!--.*?-->', '', html)

    # Remove noisy wrapper tags but keep content
    html = re.sub(r'(?is)</?(?:section|div|span|font|o:p)[^>]*>', '', html)

    # Convert some legacy tags
    html = re.sub(r'(?is)<\s*/\s*b\s*>', '</strong>', html)
    html = re.sub(r'(?is)<\s*b\b[^>]*>', '<strong>', html)
    html = re.sub(r'(?is)<\s*/\s*i\s*>', '</em>', html)
    html = re.sub(r'(?is)<\s*i\b[^>]*>', '<em>', html)

    # Drop attributes from allowed tags, keep only href/src and a few safe attrs
    def keep_tag(m: re.Match) -> str:
        slash, tag, attrs = m.group(1), m.group(2).lower(), m.group(3) or ''
        if tag not in ALLOWED:
            return ''
        if slash:
            return f'</{tag}>'
        if tag == 'a':
            href = extract(attrs, r'href\s*=\s*["\']([^"\']+)["\']', '#')
            target = extract(attrs, r'target\s*=\s*["\']([^"\']+)["\']', '')
            rel = ' rel="noopener noreferrer"' if target == '_blank' else ''
            tgt = ' target="_blank"' if target == '_blank' else ''
            return f'<a href="{href}"{tgt}{rel}>'
        if tag == 'img':
            src = extract(attrs, r'src\s*=\s*["\']([^"\']+)["\']', '')
            alt = extract(attrs, r'alt\s*=\s*["\']([^"\']*)["\']', '')
            if not src:
                return ''
            return f'<img src="{src}" alt="{alt}" loading="lazy" decoding="async">'
        if tag == 'br':
            return '<br>'
        return f'<{tag}>'

    html = re.sub(r'(?is)<\s*(/?)\s*([a-z0-9:]+)([^>]*)>', keep_tag, html)

    # Cleanup broken nests and empties
    html = re.sub(r'(?is)<p>\s*(<p>)+', '<p>', html)
    html = re.sub(r'(?is)(</p>\s*){2,}', '</p>\n', html)
    html = re.sub(r'(?is)<p>\s*(?:<br>\s*)*</p>', '', html)
    html = re.sub(r'(?is)<p>\s*&nbsp;\s*</p>', '', html)
    html = re.sub(r'\n{3,}', '\n\n', html)

    # Ensure there is enough paragraph structure for reading
    html = html.strip()
    html = promote_h2(html)
    return html


def promote_h2(html: str) -> str:
    heading_whitelist = {
        '天才的诞生',
        '人生的转折',
        '兰根的决定',
        '对抗心理陷阱',
        '生死之间',
        '路从无到有',
        '数次尝试',
        '“奇怪”也是一种天赋',
        '中文的难学是出了名的',
        '漢字是最具生命力的文字',
        '为漢字拉丁化进行的简化',
        '简化字的秘密武器',
    }

    def repl(m: re.Match) -> str:
        raw = m.group(1)
        text = strip_tags(raw).strip().strip('：:')
        compact = re.sub(r'\s+', '', text)
        compact = compact.replace('“', '').replace('”', '').replace('"', '').replace('‘', '').replace('’', '')
        # Auto-promote chapter-like lines to h2:
        # - explicit whitelist
        # - "简化成果X：..."
        if (
            text in heading_whitelist
            or compact == '奇怪也是一种天赋'
            or re.match(r'^简化成果[一二三四五六七八九十0-9]+[：:].*$', text)
            or re.match(r'^[第[一二三四五六七八九十0-9].{0,20}$', text)
            or (
                3 <= len(compact) <= 20
                and not re.search(r'[。！？：；,.!?;]', compact)
                and not re.search(r'^(今天|后来|因此|因为|所以|如果|我们|他们|她们|他在|她在)', compact)
            )
        ):
            return f'<h2>{text}</h2>'
        return m.group(0)

    # Paragraph headings from legacy content, including <strong> wrappers.
    html = re.sub(r'(?is)<p>\s*(.*?)\s*</p>', repl, html)
    return html


def parse_prev_next(raw: str):
    prev_href = extract(raw, r'<div class="prev">上一篇：<a href="([^"]+)"', '')
    prev_title = extract(raw, r'<div class="prev">上一篇：<a [^>]*>(.*?)</a>', '')
    next_href = extract(raw, r'<div class="next">下一篇：<a href="([^"]+)"', '')
    next_title = extract(raw, r'<div class="next">下一篇：<a [^>]*>(.*?)</a>', '')
    return prev_href, strip_tags(prev_title), next_href, strip_tags(next_title)


def build_post(filename: str):
    raw_path = RAW / filename
    out_path = ROOT / filename
    raw = raw_path.read_text(encoding='utf-8', errors='ignore')

    title = strip_tags(extract(raw, r'<h1[^>]*>(.*?)</h1>', Path(filename).stem))
    canonical = extract(raw, r'<link rel="canonical" href="([^"]+)"', f'https://mitaojun.com/{filename}')
    desc = strip_tags(extract(raw, r'<meta name="description" content="([^"]*)"', ''))
    time_full = extract(raw, r'<time[^>]*datetime="([0-9T:\-Z+]+)"', '')
    date_ymd = time_full[:10] if len(time_full) >= 10 else datetime.now().strftime('%Y-%m-%d')

    body_raw = extract(raw, r'<div class="text post-content"[^>]*>(.*?)</div>\s*<div class="text_add">', '')
    body = clean_body(body_raw)
    first_text = strip_tags(body)
    if not desc:
        desc = first_text[:78]
    desc_short = desc[:45]

    first_img = extract(body, r'<img[^>]*src="([^"]+)"', PUBLISHER_LOGO)
    modified = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    published = f'{date_ymd}T00:00:00+08:00'

    prev_href, prev_title, next_href, next_title = parse_prev_next(raw)

    tpl = TEMPLATE_PATH.read_text(encoding='utf-8')
    replacements = {
        '__POST_TITLE__': title,
        '__POST_DESCRIPTION__': desc,
        '__POST_DESCRIPTION_SHORT__': desc_short,
        '__POST_URL__': canonical,
        '__POST_IMAGE_URL__': first_img,
        '__POST_PUBLISHED_AT_ISO8601__': published,
        '__POST_MODIFIED_AT_ISO8601__': modified,
        '__POST_AUTHOR__': AUTHOR,
        '__PUBLISHER_LOGO_URL__': PUBLISHER_LOGO,
        '__POST_DATE_YYYY-MM-DD__': date_ymd,
    }
    out = tpl
    for k, v in replacements.items():
        out = out.replace(k, v)

    out = out.replace(
        '<meta name="robots" content="noindex,follow">',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">'
    )

    # Replace sample article body with real body
    out = re.sub(
        r'(<h1>.*?</h1>\s*)(.*?)(\s*<p class="copyright-note">)',
        lambda m: m.group(1) + '\n\n          ' + body + '\n\n          ' + m.group(3).strip(),
        out,
        flags=re.I | re.S,
    )

    # Prev/next links
    if prev_href and prev_title:
        out = re.sub(
            r'<a href="[^"]+" class="prev"><span class="nav-label">上一篇</span><span class="nav-title">.*?</span></a>',
            f'<a href="{prev_href}" class="prev"><span class="nav-label">上一篇</span><span class="nav-title">{prev_title}</span></a>',
            out,
            flags=re.S,
        )
    if next_href and next_title:
        out = re.sub(
            r'<a href="[^"]+" class="next"><span class="nav-label">下一篇</span><span class="nav-title">.*?</span></a>',
            f'<a href="{next_href}" class="next"><span class="nav-label">下一篇</span><span class="nav-title">{next_title}</span></a>',
            out,
            flags=re.S,
        )

    out_path.write_text(out, encoding='utf-8')
    print(f'Wrote {out_path.name} ({title})')


if __name__ == '__main__':
    posts = [
        p.name for p in sorted(RAW.glob('*.html'))
        if p.name not in EXCLUDE_PAGES
    ]
    for post in posts:
        build_post(post)
    print(f'Total generated: {len(posts)}')
