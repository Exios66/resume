"""Charts drawn from report tables by scripts/charts.lua.

Static checks on styles.css and the rendered docs/; no browser needed.
Design: .github/specs/2026-11-07-interactive-charts-design.md
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "styles.css").read_text(encoding="utf-8")

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


if __name__ == "__main__":
    unittest.main()
