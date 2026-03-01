#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path('/Users/cc801/Documents/mitaojun-github-archive')
EXCLUDE = {
    'index.html', 'archive.html', 'contact.html', 'contact-success.html',
    'post-template.html', 'post-minimal.html'
}


def strip_tags(s: str) -> str:
    s = re.sub(r'(?is)<[^>]+>', ' ', s)
    s = s.replace('&nbsp;', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def cleanup_block(block: str) -> tuple[str, dict]:
    stats = {
        'empty_p_removed': 0,
        'dup_p_removed': 0,
        'heading_quote_fixed': 0,
        'leading_br_trimmed': 0,
    }

    # Normalize quote spacing in h2 like: “ 奇怪 ” -> “奇怪”
    before = block
    block = re.sub(r'<h2>\s*“\s*([^”]+?)\s*”\s*', r'<h2>“\1”', block)
    if block != before:
        stats['heading_quote_fixed'] += 1

    # Remove excessive leading <br> right after opening area
    before = block
    block = re.sub(r'^(\s*<br>\s*)+', '', block)
    if block != before:
        stats['leading_br_trimmed'] += 1

    # Remove <br> at start of paragraph and normalize paragraph edges
    block = re.sub(r'(?is)<p>\s*(?:<br>\s*)+', '<p>', block)
    block = re.sub(r'(?is)(?:<br>\s*)+</p>', '</p>', block)

    # Remove empty paragraphs
    def rm_empty_p(m: re.Match) -> str:
        inner = m.group(1)
        plain = strip_tags(inner)
        if plain:
            return m.group(0)
        stats['empty_p_removed'] += 1
        return ''

    block = re.sub(r'(?is)<p>(.*?)</p>', rm_empty_p, block)

    # Remove adjacent duplicate paragraphs by plain text
    parts = []
    last_p_text = None
    i = 0
    for m in re.finditer(r'(?is)<p>(.*?)</p>', block):
        start, end = m.span()
        parts.append(block[i:start])
        p_html = m.group(0)
        p_text = strip_tags(m.group(1))
        if p_text and p_text == last_p_text:
            stats['dup_p_removed'] += 1
        else:
            parts.append(p_html)
            if p_text:
                last_p_text = p_text
        i = end
    parts.append(block[i:])
    block = ''.join(parts)

    # Collapse extra blank lines
    block = re.sub(r'\n{3,}', '\n\n', block)
    return block.strip(), stats


def process_file(path: Path) -> dict:
    html = path.read_text(encoding='utf-8', errors='ignore')
    m = re.search(r'(<h1>.*?</h1>\s*)(.*?)(\s*<p class="copyright-note">)', html, re.I | re.S)
    if not m:
        return {'changed': False}

    prefix, body, suffix = m.group(1), m.group(2), m.group(3)
    new_body, stats = cleanup_block(body)

    changed = new_body != body
    if changed:
        new_html = html[:m.start(2)] + new_body + html[m.end(2):]
        path.write_text(new_html, encoding='utf-8')

    stats['changed'] = changed
    return stats


def main():
    files = [p for p in sorted(ROOT.glob('*.html')) if p.name not in EXCLUDE]
    total = 0
    changed_files = 0
    agg = {
        'empty_p_removed': 0,
        'dup_p_removed': 0,
        'heading_quote_fixed': 0,
        'leading_br_trimmed': 0,
    }

    for f in files:
        total += 1
        s = process_file(f)
        if s.get('changed'):
            changed_files += 1
        for k in agg:
            agg[k] += int(s.get(k, 0))

    print(f'Processed {total} files, changed {changed_files} files')
    print('Stats:', agg)


if __name__ == '__main__':
    main()
