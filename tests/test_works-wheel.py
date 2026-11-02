"""Regression tests for the staged works-wheel.js changes.

The wheel renders its own DOM at runtime, so these tests validate the data it
projects, the assets it loads, and the removal of the old VIEW badge.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "works-wheel.js").read_text(encoding="utf-8")

EXPECTED_WORKS = [
    ("Animated Portfolio", "Landing Page Assets/Portfolio.png", "#animated-portfolio"),
    ("Tape Design", "Landing Page Assets/Tape.png", "#tape-design"),
    ("Forest Beauty", "Landing Page Assets/Forest.png", "#forest-beauty"),
    ("Forma Web", "Landing Page Assets/Forma.png", "#forma-web"),
    ("Lycoris", "Landing Page Assets/Lycoris.png", "#lycoris"),
    ("Mountain Range", "Landing Page Assets/Mountain.png", "#mountain-range"),
]

REMOVED_TRACES = [
    "Aether",
    "Afterform",
    "Maison",
    "Éléara",
    "Eleara",
    "Cognitive Workspace",
    "Brutalist",
    "Sandstone",
    "Jewellery",
    "Place Vendôme",
    "Landing Page Assest",
    "Screenshot 2026-10-20",
]


def _array_body() -> str:
    match = re.search(r"export const DEFAULT_WORKS\s*=\s*\[(.*?)\n\];", SOURCE, re.S)
    assert match is not None, "DEFAULT_WORKS array not found in works-wheel.js"
    return match.group(1)


def _blocks() -> list[str]:
    blocks = re.findall(r"\{(.*?)\n  \}", _array_body(), re.S)
    assert blocks, "no works-wheel entries found"
    return blocks


def _field(block: str, name: str) -> str:
    match = re.search(rf'{name}:\s*(["\'])(.*?)\1', block, re.S)
    assert match is not None, f"missing field {name!r} in works entry"
    return match.group(2)


def _list_field(block: str, name: str) -> list[str]:
    match = re.search(rf"{name}:\s*\[(.*?)\]", block, re.S)
    assert match is not None, f"missing list field {name!r} in works entry"
    return re.findall(r'["\']([^"\']+)["\']', match.group(1))


WORKS = [
    {
        "title": _field(block, "title"),
        "subtitle": _field(block, "subtitle"),
        "description": _field(block, "description"),
        "image": _field(block, "image"),
        "src": _field(block, "src"),
        "href": _field(block, "href"),
        "stats": _field(block, "stats"),
        "tools": _list_field(block, "tools"),
        "deliverables": _list_field(block, "deliverables"),
    }
    for block in _blocks()
]


def test_wheel_exposes_the_six_expected_landing_pages():
    assert len(WORKS) == len(EXPECTED_WORKS) == 6
    assert [(work["title"], work["image"], work["href"]) for work in WORKS] == EXPECTED_WORKS


def test_image_and_src_point_to_the_same_existing_thumbnail():
    for work in WORKS:
        assert work["image"] == work["src"]
        path = ROOT / work["image"]
        assert path.is_file(), f"missing wheel thumbnail: {work['image']}"
        assert path.stat().st_size > 10_000, f"thumbnail looks empty: {work['image']}"
        assert path.read_bytes()[:8].startswith(b"\x89PNG\r\n\x1a\n"), (
            f"wheel thumbnail is not a PNG: {work['image']}"
        )


def test_thumbnails_live_in_the_renamed_assets_folder():
    assert (ROOT / "Landing Page Assets").is_dir()
    assert not (ROOT / "Landing Page Assest").exists()
    assert "Landing Page Assest" not in SOURCE


def test_old_project_copy_is_gone():
    for trace in REMOVED_TRACES:
        assert trace.lower() not in SOURCE.lower(), f"old trace still present: {trace}"


def test_each_entry_has_complete_modal_metadata():
    for work in WORKS:
        assert work["subtitle"].strip()
        assert work["description"].strip()
        assert work["stats"].strip()
        assert len(work["tools"]) >= 3
        assert len(work["deliverables"]) >= 3


def test_hrefs_are_unique_in_page_slugs():
    hrefs = [work["href"] for work in WORKS]
    assert len(set(hrefs)) == len(hrefs)
    for href in hrefs:
        assert re.fullmatch(r"#[a-z0-9-]+", href), f"unexpected href: {href}"


def test_view_badge_and_action_option_are_removed():
    assert "View ↗" not in SOURCE
    assert "↗" not in SOURCE
    assert "${action}" not in SOURCE
    assert re.search(r"\baction\b", SOURCE) is None


def test_title_only_badge_is_still_rendered():
    assert "cardInfo.innerHTML" in SOURCE
    badge = re.search(r"cardInfo\.innerHTML\s*=\s*`(.*?)`;", SOURCE, re.S)
    assert badge is not None
    assert "${item.title}" in badge.group(1)
    assert "VIEW" not in badge.group(1).upper()


def test_wheel_module_still_exports_the_engine():
    assert "export function initWorksWheel(" in SOURCE
    assert "options.items || DEFAULT_WORKS" in SOURCE
