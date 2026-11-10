"""Preserve the original scholarly source inventory during citation formatting."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def test_natd_source_notes_preserve_every_existing_bibliographic_entry():
    inventory = json.loads((ROOT / "tests/fixtures/natd-citations.json").read_text())
    source = (ROOT / "projects/natd/report.qmd").read_text()
    notes = dict(re.findall(r"^\[\^(cite\d+)\]: (.+)$", source, re.M))
    assert len(inventory) == len(notes) == 17
    assert notes == {row["id"]: row["full"] for row in inventory}
    literature = source.split("## Literature review\n", 1)[1].split("\n## Method", 1)[0]
    assert re.findall(r"\[\^(cite\d+)\]", literature) == [row["id"] for row in inventory]
