"""Regression tests for the staged flex-carousel.js changes.

The carousel is an ES module that imports WebGL helpers from a CDN, so these
tests validate its exported data and asset references instead of executing it.
"""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "flex-carousel.js").read_text(encoding="utf-8")

EXPECTED_ITEMS = [
    {
        "title": "Portfolio Website",
        "subtitle": "3D Premium Experience",
        "description": "3D Premium Experience",
        "link": "https://harshithsriramoju.vercel.app",
        "src": "Project Images/Portfolio.png",
    },
    {
        "title": "Happy Birthday",
        "subtitle": "Web Experienced Birthday Gift",
        "description": "Web Experienced Birthday Gift",
        "link": "https://happybirthday-three-red.vercel.app",
        "src": "Project Images/Happybirthday.png",
    },
    {
        "title": "Ganesh Aagman",
        "subtitle": "Devotional Welcome of God",
        "description": "Devotional Welcome of God",
        "link": "https://aagman-eta.vercel.app",
        "src": "Project Images/Ganeshaagman.png",
    },
    {
        "title": "Ember & Roast",
        "subtitle": "Warm Cafe Experience",
        "description": "Warm Cafe Experience",
        "link": "https://coffee-shop-website-gilt.vercel.app",
        "src": "Project Images/Emberandroast.png",
    },
    {
        "title": "Engineering College",
        "subtitle": "Professional College Website",
        "description": "Professional College Website",
        "link": "https://code-revive-gold.vercel.app",
        "src": "Project Images/Engineeringclg.png",
    },
    {
        "title": "DukaanGo",
        "subtitle": "Hyperlocal eCommerce Platform",
        "description": "Hyperlocal eCommerce Platform",
        "link": "https://dukaan-go.vercel.app",
        "src": "Project Images/Dukaango.jpeg",
    },
]

REMOVED_PROJECT_TRACES = [
    "Cafe Website",
    "Design Studio",
    "Photographer Portfolio",
    "Sen Cruzo",
    "mochaandmiso",
    "jishnumondal",
    "echo-design-studio",
    "julianvance",
]


def _items_array_body() -> str:
    match = re.search(r"export const DEFAULT_ITEMS\s*=\s*\[(.*?)\n\];", SOURCE, re.S)
    assert match is not None, "DEFAULT_ITEMS array not found in flex-carousel.js"
    return match.group(1)


def _item_blocks() -> list[str]:
    blocks = re.findall(r"\{(.*?)\}", _items_array_body(), re.S)
    assert blocks, "no carousel items found"
    return blocks


def _field(block: str, name: str) -> str:
    match = re.search(rf"{name}:\s*(['\"])(.*?)\1", block, re.S)
    assert match is not None, f"missing field {name!r} in carousel item"
    return match.group(2)


ITEMS = [
    {
        "title": _field(block, "title"),
        "subtitle": _field(block, "subtitle"),
        "description": _field(block, "description"),
        "link": _field(block, "link"),
        "src": _field(block, "src"),
        "alt": _field(block, "alt"),
    }
    for block in _item_blocks()
]


def test_carousel_exposes_the_six_expected_projects():
    assert len(ITEMS) == len(EXPECTED_ITEMS) == 6
    assert ITEMS == [
        {
            "title": expected["title"],
            "subtitle": expected["subtitle"],
            "description": expected["description"],
            "link": expected["link"],
            "src": expected["src"],
            "alt": expected["title"],
        }
        for expected in EXPECTED_ITEMS
    ]


def test_carousel_projects_keep_their_order():
    assert [item["title"] for item in ITEMS] == [expected["title"] for expected in EXPECTED_ITEMS]


def test_every_carousel_link_is_https_and_matches_the_expected_host():
    for item, expected in zip(ITEMS, EXPECTED_ITEMS):
        assert item["link"] == expected["link"]
        assert item["link"].startswith("https://")
        assert item["link"].rstrip("/").split("/")[2] in expected["link"]


def test_every_carousel_thumbnail_exists_and_is_a_real_image():
    for item in ITEMS:
        path = ROOT / item["src"]
        assert path.is_file(), f"missing carousel thumbnail: {item['src']}"
        assert path.stat().st_size > 10_000, f"thumbnail looks empty: {item['src']}"
        header = path.read_bytes()[:8]
        assert header.startswith(b"\x89PNG\r\n\x1a\n") or header.startswith(b"\xff\xd8\xff"), (
            f"thumbnail is neither PNG nor JPEG: {item['src']}"
        )


def test_dukaango_uses_the_jpeg_asset():
    dukaan = next(item for item in ITEMS if item["title"] == "DukaanGo")
    assert dukaan["src"].endswith("Dukaango.jpeg")
    assert "DukaanGo.png" not in SOURCE


def test_old_project_data_is_gone():
    source_lower = SOURCE.lower()
    for trace in REMOVED_PROJECT_TRACES:
        assert trace.lower() not in source_lower, f"old project trace still present: {trace}"


def test_unused_unsplash_helper_is_removed():
    assert "images.unsplash.com" not in SOURCE
    assert "export const photo" not in SOURCE


def test_carousel_caption_fields_are_non_empty():
    for item in ITEMS:
        assert item["title"].strip()
        assert item["subtitle"].strip()
        assert item["description"].strip()
        assert item["alt"] == item["title"]


def test_carousel_module_still_exports_the_engine():
    assert "export function initFlexCarousel(" in SOURCE
    assert "options.items && options.items.length ? options.items : DEFAULT_ITEMS" in SOURCE
