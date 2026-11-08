#!/usr/bin/env python3
"""Maintain references for the existing state-change essay without regenerating it.

Default: check only. --write updates this fixed set of 18 HTML and Markdown files.
Content reconstruction is still a draft; this does not promote the new builder.
"""
import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://genai-ron.jp/article/state-change/'
NAMES = ['index', *[f'chapter-{i:02}' for i in range(1, 17)], 'bibliography']
TARGETS = {f'{folder}/article/state-change/{name}.{ext}'
           for folder, ext in [('site', 'html'), ('content', 'md')] for name in NAMES}
SUPPORT = {'scripts/maintain_state_change_metadata.py',
           'scripts/test_state_change_maintenance.py',
           'scripts/validate_state_change_visual.js',
           '.github/workflows/validate-publishing-structure.yml',
           'scripts/validate_new_document_publication_pr.py',
           'docs/maintenance/state-change-ai-readability.md'}


def transform_html(text, name):
    text = text.replace('href="state-change/"', 'href="./"')
    text = text.replace('href="../notes/themes.html"', 'href="../../notes/themes.html"')
    if name == 'index':
        text = text.replace('同じ会話へは戻れ">', '同じ会話へは戻れない。">')
    canonical = BASE + ('' if name == 'index' else name + '.html')
    if '<link rel="canonical"' not in text:
        text = text.replace('  <link rel="stylesheet"', f'  <link rel="canonical" href="{canonical}">\n  <link rel="stylesheet"', 1)
    if '<meta name="author"' not in text:
        text = text.replace('  <title>', '  <meta name="author" content="Taku">\n  <title>', 1)
    if '<p class="author">' not in text:
        text = text.replace('</h1>', '</h1>\n    <p class="author">著者：Taku｜生成AI論</p>', 1)
    def heading(match):
        attrs, body = match.group(1), match.group(2)
        if re.search(r'\bid\s*=', attrs):
            return match.group(0)
        # Use existing section labels, not positional counts that shift on insertion.
        label = re.match(r'([0-9]+|[A-Z])\.', body)
        anchor = 'section-' + label.group(1).lower() if label else ('contents' if body == '目次' else None)
        if anchor is None:
            raise ValueError('Unrecognized section heading: ' + body)
        return f'<h2{attrs} id="{anchor}">{body}</h2>'
    return re.sub(r'<h2([^>]*)>(.*?)</h2>', heading, text, flags=re.S)


def transform_markdown(text, name):
    front, body = text.split('---', 2)[1:]
    canonical = BASE + ('' if name == 'index' else name + '.html')
    front = re.sub(r'^canonical: null$', f'canonical: "{canonical}"', front, flags=re.M)
    front = front.replace('  canonical: "absent"', '  canonical: "public_url_verified_2026-11-08"')
    if not re.search(r'^author:', front, re.M):
        front = front.replace('\ncanonical:', '\nauthor: "Taku"\ncanonical:', 1)
        front = front.replace('metadata_provenance:\n', 'metadata_provenance:\n  author: "article_index_visible_author"\n', 1)
    if name == 'index':
        front = front.replace('同じ会話へは戻れ"', '同じ会話へは戻れない。"')
    body = body.replace('](../notes/themes.html)', '](../../notes/themes.html)')
    # Keep source_html_sha256 as the historical extraction hash, not a claim of re-extraction.
    return '---' + front + '---' + body


def validate_changes(files, read_base, read_current):
    """Accept only the exact documented transformation of pre-existing pages."""
    if not files or not (set(files) & TARGETS):
        raise ValueError('No state-change pages changed')
    unexpected = set(files) - TARGETS - SUPPORT
    if unexpected:
        raise ValueError('Unrelated changes: ' + ', '.join(sorted(unexpected)))
    for path in sorted(TARGETS):
        before = read_base(path)  # missing old pages fail: this lane cannot publish new pages
        transform = transform_html if path.startswith('site/') else transform_markdown
        expected = transform(before, Path(path).stem)
        if read_current(path) != expected:
            raise ValueError('Not the permitted metadata/reference transformation: ' + path)
    print('PASS: 36 existing files match the exact reference/metadata transformation')


def validate_revision(base_ref, files):
    base = subprocess.check_output(['git', 'merge-base', base_ref, 'HEAD'], cwd=ROOT, text=True).strip()
    def read_base(path):
        return subprocess.check_output(['git', 'show', f'{base}:{path}'], cwd=ROOT).decode('utf-8')
    validate_changes(files, read_base, lambda path: (ROOT / path).read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    changed = []
    for name in NAMES:
        for folder, ext, transform in [('site', 'html', transform_html), ('content', 'md', transform_markdown)]:
            path = ROOT / folder / 'article/state-change' / f'{name}.{ext}'
            before = path.read_text()
            after = transform(before, name)
            if before != after:
                changed.append(str(path.relative_to(ROOT)))
                if args.write:
                    path.write_text(after)
    for path in changed:
        print(('updated: ' if args.write else 'needs update: ') + path)
    if changed and not args.write:
        raise SystemExit(1)
    print('PASS: fixed-scope metadata maintenance is current')


if __name__ == '__main__':
    main()
