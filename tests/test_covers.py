"""Project cover motifs: one per project, theme-coloured, reproducible, and wired into the cards."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "partials" / "covers"
PROJECTS = sorted(p.stem for p in (ROOT / "projects").glob("*.qmd") if p.stem != "index")


def test_every_project_has_a_cover_and_the_index_uses_it():
    index = (ROOT / "projects" / "index.qmd").read_text()
    for slug in PROJECTS:
        assert (COVERS / f"{slug}.svg").is_file(), slug
        assert f'::: {{.card cover="{slug}"}}' in index, slug
    assert sorted(p.stem for p in COVERS.glob("*.svg")) == PROJECTS


def test_covers_take_colour_from_the_theme_only():
    for svg in COVERS.glob("*.svg"):
        text = svg.read_text()
        assert text.startswith('<svg viewBox="0 0 320 120" '), svg.name
        assert not re.search(r'#[0-9a-fA-F]{3,8}\b|rgb\(|\bstyle=|\bid=|\b(fill|stroke)="', text), svg.name
        assert "<text" not in text and "<script" not in text, svg.name


def test_covers_match_their_generator(tmp_path):
    before = {p.name: p.read_bytes() for p in COVERS.glob("*.svg")}
    subprocess.run([sys.executable, str(ROOT / "scripts" / "make-covers.py")], check=True, capture_output=True)
    assert {p.name: p.read_bytes() for p in COVERS.glob("*.svg")} == before


def test_built_cards_show_decorative_covers():
    for page, count in (("index.html", 4), ("projects/index.html", len(PROJECTS))):
        html = (ROOT / "docs" / page).read_text()
        assert html.count('<div class="card-cover" aria-hidden="true"><svg') == count, page
        assert "cover=" not in html, page
