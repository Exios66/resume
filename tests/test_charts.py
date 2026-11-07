"""Charts drawn from report tables by scripts/charts.lua.

Static checks on styles.css and the rendered docs/; no browser needed.
Design: .github/specs/2026-11-07-interactive-charts-design.md
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")
DOCS = ROOT / "docs"

# Built page -> number of charts it carries.
PAGES = {
    "projects/natd.html": 1,
    "projects/natd/report.html": 1,
    "projects/mailroom-ml/report.html": 1,
    "projects/mailroom-corpus-eda/report.html": 1,
    "projects/rvl-cdip-classifier.html": 1,
    "projects/mapreduce-reloaded.html": 1,
    "projects/langtons-ant.html": 1,
}
FIGURE = re.compile(r'<figure class="chart chart-\w+">.*?</figure>', re.S)
TABLE = re.compile(r"<table\b.*?</table>", re.S)


def page(path):
    return (DOCS / path).read_text(encoding="utf-8")


def numbers(text):
    """Every number in text as a float (Unicode minus, commas and signs handled)."""
    text = text.replace("\u2212", "-")
    return [float(n.replace(",", "")) for n in re.findall(r"-?\d+(?:,\d{3})*(?:\.\d+)?", text)]


def strip_tags(html):
    return re.sub(r"<[^>]+>", " ", html)


def chart_and_table(html):
    """Yield (figure_html, table_html) for every chart, requiring the table to follow it."""
    for match in FIGURE.finditer(html):
        rest = html[match.end():].lstrip()
        table = TABLE.match(rest)
        yield match.group(0), table.group(0) if table else None

LIGHT = {"--chart-1": "#008b9a", "--chart-2": "#4f5fc4", "--chart-1-soft": "#6cb2bb"}
DARK = {"--chart-1": "#2aa3b0", "--chart-2": "#7c86f0", "--chart-1-soft": "#1f6f78"}


def block(css, opener):
    """Return the body of the first rule or at-rule that starts with opener."""
    start = css.index(opener)
    depth, i = 0, css.index("{", start)
    begin = i
    while True:
        depth += {"{": 1, "}": -1}.get(css[i], 0)
        if depth == 0:
            return css[begin + 1:i]
        i += 1


class ChartTokenTests(unittest.TestCase):
    def assert_tokens(self, body, values):
        for token, value in values.items():
            self.assertRegex(body, rf"{token}:\s*{re.escape(value)}\b", token)

    def test_chart_tokens_in_every_theme_block(self):
        self.assert_tokens(block(CSS, ":root {"), LIGHT)
        self.assert_tokens(block(CSS, ':root:not([data-theme="light"])'), DARK)
        self.assert_tokens(block(CSS, ':root[data-theme="dark"]'), DARK)
        print_tokens = re.search(r":root:root:root[^{}]*\{([^{}]*)\}", block(CSS, "@media print")).group(1)
        self.assert_tokens(print_tokens, LIGHT)



class ChartPageTests(unittest.TestCase):
    def test_each_page_has_its_chart(self):
        for path, expected in PAGES.items():
            with self.subTest(path=path):
                pairs = list(chart_and_table(page(path)))
                self.assertEqual(len(pairs), expected)
                for _, table in pairs:
                    self.assertIsNotNone(table, "the chart's table must follow it")

    def test_tip_values_match_table_cells(self):
        for path in PAGES:
            for figure, table in chart_and_table(page(path)):
                cells = set(numbers(strip_tags(table)))
                tips = re.findall(r'data-tip-value="([^"]*)"', figure)
                self.assertTrue(tips, path)
                for tip in tips:
                    for value in numbers(tip):
                        with self.subTest(path=path, tip=tip):
                            self.assertTrue(any(abs(value - c) < 1e-9 for c in cells), f"{value} not in table")

    def test_new_tables_come_from_prose(self):
        for path, header in (("projects/rvl-cdip-classifier.html", "Before"),
                             ("projects/mapreduce-reloaded.html", "Speedup")):
            html = page(path)
            for figure, table in chart_and_table(html):
                if f">{header}<" not in table:
                    continue
                prose = strip_tags(html.replace(figure, "").replace(table, ""))
                body = re.sub(r"<thead>.*?</thead>", "", table, flags=re.S)
                for cell in re.findall(r"<td[^>]*>(.*?)</td>", body, re.S):
                    for token in re.findall(r"\d+(?:\.\d+)?(?:%|×)?", strip_tags(cell)):
                        with self.subTest(path=path, token=token):
                            self.assertIn(token, prose)
                break
            else:
                self.fail(f"{path}: no chart table with a {header} column")

    def test_chart_shapes_have_fallback_paint(self):
        for path in PAGES:
            for figure, _ in chart_and_table(page(path)):
                for shape in re.findall(r"<(?:rect|circle|line|path)\b[^>]*>", figure):
                    with self.subTest(path=path, shape=shape[:60]):
                        self.assertRegex(shape, r'\bfill="[^"]+"')
                        self.assertRegex(shape, r'\bstroke="[^"]+"')


if __name__ == "__main__":
    unittest.main()
