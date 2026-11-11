"""Source-backed project wiring and freshness regressions, without network access."""

import xml.etree.ElementTree as ET

import test_links as checks
from test_portfolio_additions import ContentParser

PAGE = checks.DOCS / "projects/neuron-atlas.html"
CODE = "https://github.com/Exios66/LLM_Viz"
LIVE = "https://exios66.github.io/LLM_Viz/"
REVISION = "a58000861b424280158cea728cf7b29edaf385d1"


def test_project_is_discoverable_and_uses_the_branch_project_not_a_different_repo():
    for name in ("index.html", "projects/index.html", "about.html"):
        page = checks.DOCS / name
        assert PAGE.resolve() in checks.linked_targets(page)
    parser = ContentParser(PAGE)
    hrefs = [checks.attr(a, "href") for tag, a, _ in parser.elements if tag == "a"]
    assert CODE in hrefs and LIVE in hrefs
    assert f"{CODE}/tree/{REVISION}" in hrefs
    assert f"{CODE}/tree/neuron-atlas" in hrefs
    nav = next(a for tag, a, _ in parser.elements if "project-nav" in checks.classes(a))
    assert [checks.attr(a, "href") for tag, a in parser.children(nav)
            if tag == "a" and checks.attr(a, "aria-current") == "page"] == ["../projects/neuron-atlas.html"]
    locations = [n.text for n in ET.parse(checks.DOCS / "sitemap.xml").findall("{*}url/{*}loc")]
    assert locations.count("https://exios66.github.io/resume/projects/neuron-atlas.html") == 1


def test_metrics_keep_live_and_recorded_models_and_null_comparison_separate():
    parser = ContentParser(PAGE)
    text = " ".join(t for t, _ in parser.text_fragments)
    for claim in ("8,192", "2,048", "41", "recorded data", "do not run live",
                  "47 of 48", "not a corrected significance test", "6 November 2026"):
        assert claim in text
    assert not (checks.DOCS / "projects/neuron-atlas/report.html").exists()


def test_figure_is_local_described_and_published_byte_for_byte():
    parser = ContentParser(PAGE)
    images = [a for tag, a, _ in parser.elements if tag == "img"]
    assert len(images) == 1
    assert len(checks.attr(images[0], "alt").split()) > 20
    source = checks.ROOT / "projects/neuron-atlas/figures/steering-studio.jpg"
    assert source.read_bytes() == (checks.DOCS / source.relative_to(checks.ROOT)).read_bytes()
    assert REVISION in source.with_name("MANIFEST.txt").read_text()


def test_m9c_is_current_and_m9b_report_is_explicitly_historical():
    study = ContentParser(checks.DOCS / "projects/mailroom-ml.html")
    text = " ".join(t for t, _ in study.text_fragments)
    for claim in ("95.98%", "39.01%", "not production fast-path coverage",
                  "229 of 310", "Earlier results: M9b"):
        assert claim in text
    report = ContentParser(checks.DOCS / "projects/mailroom-ml/report.html")
    assert "Historical report through M9b" in " ".join(t for t, _ in report.text_fragments)


def test_quick_issue_fixes_keep_model_data_citation_and_degree_distinct():
    study = checks.DOCS / "projects/mailroom-ml.html"
    hrefs = [checks.attr(a, "href") for tag, a, _ in checks.parse(study) if tag == "a"]
    assert "https://huggingface.co/datasets/Lucius-Morningstar/mailroom-modernbert-training" in hrefs
    assert "https://huggingface.co/Lucius-Morningstar/mailroom-modernbert-classifier/tree/m9c-20261014-113614" in hrefs
    corpus = ContentParser(checks.DOCS / "projects/mailroom-corpus-eda.html")
    citation = next(a for _, a, _ in corpus.elements if checks.attr(a, "id") == "dataset-citation")
    assert citation is not None
    assert "https://huggingface.co/datasets/Lucius-Morningstar/mailroom-dataset/tree/v9.2" in [
        checks.attr(a, "href") for tag, a, _ in corpus.elements if tag == "a"]
    for name in ("resume.html", "about.html"):
        parser = ContentParser(checks.DOCS / name)
        text = " ".join(t for t, _ in parser.text_fragments)
        assert "Psychology & Data Science" not in text
        assert "Psychology: Data Science in Human Behavior" in text
    release = (checks.ROOT / ".github/release-notes/v1.0.0.md").read_text()
    assert "Historical release record" in release
    assert "current `gh-pages`" not in release
