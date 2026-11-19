"""Project social cards: motif, 1200x630 PNG, and og:image on each case study."""

from __future__ import annotations

import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COVERS = ROOT / "partials" / "covers"
OG = ROOT / "assets" / "og"
PROJECTS = ROOT / "projects"
DOCS = ROOT / "docs"
SITE = "https://exios66.github.io/resume/assets/og"


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    # IHDR is the first chunk.
    length, ctype = struct.unpack(">I4s", data[8:16])
    if ctype != b"IHDR" or length != 13:
        raise AssertionError(f"missing IHDR: {path}")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


class SocialCardTests(unittest.TestCase):
    def test_every_project_has_motif_card_and_og_image(self):
        slugs = sorted(p.stem for p in COVERS.glob("*.svg"))
        self.assertGreaterEqual(len(slugs), 14)
        for slug in slugs:
            with self.subTest(slug=slug):
                self.assertTrue((COVERS / f"{slug}.svg").is_file())
                card = OG / f"{slug}.png"
                self.assertTrue(card.is_file(), f"missing social card {card}")
                self.assertEqual(png_size(card), (1200, 630))
                case = PROJECTS / f"{slug}.qmd"
                self.assertTrue(case.is_file())
                fm = case.read_text(encoding="utf-8")
                self.assertIn(f"image: {SITE}/{slug}.png", fm)
                built = DOCS / "projects" / f"{slug}.html"
                # Built HTML is asserted only after a render that copies the new cards.
                if built.is_file() and f"/assets/og/{slug}.png" in built.read_text(encoding="utf-8"):
                    html = built.read_text(encoding="utf-8")
                    og = re.search(r'property="og:image" content="([^"]*)"', html)
                    self.assertIsNotNone(og)
                    self.assertIn(slug, og.group(1))
                    self.assertTrue(og.group(1).endswith(f"/assets/og/{slug}.png"))


if __name__ == "__main__":
    unittest.main()
