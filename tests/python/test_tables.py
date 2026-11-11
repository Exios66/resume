"""Exercise the real table filter's code fragmentation with Pandoc attributes."""
import os
from pathlib import Path
import subprocess
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]


class CodeFragments(HTMLParser):
    """Collect each inline-code fragment and its preserved attributes."""
    def __init__(self, html):
        super().__init__()
        self.fragments = []
        self.current = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'code':
            self.current = [dict(attrs), '']
            self.fragments.append(self.current)

    def handle_data(self, text):
        if self.current is not None:
            self.current[1] += text

    def handle_endtag(self, tag):
        if tag == 'code':
            self.current = None


def test_long_code_keeps_one_anchor_and_preserves_classes_and_data():
    """Preserve code text and attributes while assigning its anchor only once."""
    source = '| Item | Value |\n| --- | --- |\n| Key | `long/path/component`{#code-ref .token data-source="sample"} |\n'
    result = subprocess.run([os.environ.get('QUARTO', 'quarto'), 'pandoc',
                             '--from=markdown', '--to=html', '--lua-filter=scripts/filters/tables.lua'],
                            cwd=ROOT, input=source, capture_output=True, text=True, check=True)
    fragments = CodeFragments(result.stdout).fragments
    assert ''.join(text for _, text in fragments) == 'long/path/component'
    assert [attrs.get('id') for attrs, _ in fragments] == ['code-ref', None, None]
    assert all(attrs.get('class') == 'token' and attrs.get('data-source') == 'sample'
               for attrs, _ in fragments)
