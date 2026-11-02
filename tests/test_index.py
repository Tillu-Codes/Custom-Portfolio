"""Static regression tests for the staged index.html changes.

The site is a static single-page document, so these tests parse the shipped
markup and inline script instead of spinning up a browser.
"""

from html.parser import HTMLParser
from pathlib import Path
import re

import pytest

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
HTML = INDEX.read_text(encoding="utf-8")

EXPECTED_SOCIALS = {
    "instagram": "https://www.instagram.com/tillu_webs?vrfl=ZTExcmJobWJ5bnV1",
    "twitter": "https://x.com/sriavegna_17",
    "linkedin": (
        "https://www.linkedin.com/in/yadoji-sri-avegna-0684a0381"
        "?utm_source=share_via&utm_content=profile&utm_medium=member_android"
    ),
    "github": "https://github.com/Tillu-Codes",
}


class TagCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def parse_tags(markup: str) -> TagCollector:
    collector = TagCollector()
    collector.feed(markup)
    collector.close()
    return collector


PARSED = parse_tags(HTML)


def attr_values(tag: str, attribute: str) -> list[str]:
    return [attrs[attribute] for name, attrs in PARSED.tags if name == tag and attribute in attrs]


def test_page_identity_has_no_original_author_traces():
    assert "<title>Yadoji Sri Avegna" in HTML
    assert "Yadoji Sri Avegna" in HTML
    assert "Jishnu" not in HTML
    assert "jishnu" not in HTML
    assert "ECHO" not in HTML

    title = re.search(r"<title>(.*?)</title>", HTML, re.S)
    assert title is not None
    assert "Developer &#38; Designer" in title.group(1) or "Developer & Designer" in title.group(1)

    meta = re.search(r'<meta name="description" content="([^"]*)"', HTML)
    assert meta is not None
    assert "Yadoji Sri Avegna" in meta.group(1)


def test_all_social_links_point_to_the_owners_profiles():
    anchors = attr_values("a", "href")
    for network, url in EXPECTED_SOCIALS.items():
        matches = [href for href in anchors if href == url]
        assert len(matches) == 2, f"{network} link should appear in header and footer, found {len(matches)}"
    assert "echo__builds" not in HTML
    assert "Jishn8m" not in HTML
    assert "jishnu-mondal" not in HTML
    assert "Jishnu09-siuu" not in HTML


def test_hero_copy_and_portrait_are_updated():
    assert "DEVELOPER EST.2024" in HTML
    assert "DESIGNER EST.2000" not in HTML
    assert "assets/Hero.png" in attr_values("img", "src")
    assert all("hero_portrait" not in src for src in attr_values("img", "src"))
    assert "AVEGNA" in HTML


def test_service_deliverables_were_replaced():
    assert "DELIVERABLES: FULL RESPONSIVE WEB DESIGNS, INTERACTIVE WEBSITES" in HTML
    assert "DELIVERABLES: CUSTOM 3D/GRAPHICS, Interactive Landing Pages" in HTML
    assert "FIGMA SYSTEM" not in HTML
    assert "WEBFLOW CODE" not in HTML


def test_about_timeline_milestones_are_updated():
    for expected in (
        "Delivered 10+ projects across diverse domains",
        "Implemented Interactive 3D Infrastructure",
        "Completed 300+ hours of hands-on development",
        "Mastered Python, Web and 3D development",
    ):
        assert expected in HTML
    for removed in (
        "Delivered 20+ projects across diverse industries",
        "Implemented CI/CD pipelines and cloud architecture",
        "Completed 500+ hours",
        "Mastered React, Node.js, and TypeScript ecosystem",
    ):
        assert removed not in HTML


def test_footer_credit_is_the_owner():
    assert "DESIGN BY YADOJI SRI AVEGNA" in HTML
    assert "DESIGN BY JISHNU MONDAL" not in HTML


def test_contact_form_posts_to_the_owners_inbox():
    assert 'id="contact-form"' in HTML
    assert "sriavegnayadoji@gmail.com" in HTML
    assert "https://formsubmit.co/ajax/${CONTACT_EMAIL}" in HTML
    assert "fetch(CONTACT_ENDPOINT" in HTML

    form_fields = {attrs.get("name") for name, attrs in PARSED.tags if name in {"input", "select", "textarea"}}
    assert {"name", "email", "service", "message", "_honey"} <= form_fields

    submit = [attrs for name, attrs in PARSED.tags if name == "button" and attrs.get("type") == "submit"]
    assert any(attrs.get("id") == "contact-submit-btn" for attrs in submit)


def test_contact_submit_only_reports_success_after_the_request():
    match = re.search(r"async function submitContactForm\(e\) \{(.*?)\n    \}", HTML, re.S)
    assert match is not None, "submitContactForm should be an async function"
    body = match.group(1)
    assert "await fetch(CONTACT_ENDPOINT" in body
    assert "form.reset()" in body
    assert "catch (err)" in body
    success_position = body.find('has been sent')
    send_position = body.find("await fetch")
    assert send_position != -1 and success_position > send_position


def test_featured_projects_and_landing_pages_are_wired_to_their_modules():
    assert "import { initFlexCarousel, DEFAULT_ITEMS } from './flex-carousel.js'" in HTML
    assert "import { initWorksWheel, DEFAULT_WORKS } from './works-wheel.js'" in HTML
    assert 'id="flex-carousel-container"' in HTML
    assert 'id="works-wheel-container"' in HTML


def test_dead_template_code_and_cart_ui_are_removed():
    for removed in (
        "cart-modal",
        "SHOPPING BAG",
        "cart-badge",
        "projectsData",
        "filterProjects",
        "toggleHeart",
        "triggerSolarAction",
        "NEXUS AI ANALYTICS PLATFORM",
        "SOLAR PANEL MOBILE APP",
    ):
        assert removed not in HTML


def test_every_local_asset_reference_exists():
    refs = set()
    for tag in ("img", "script", "link"):
        for value in attr_values(tag, "src") + attr_values(tag, "href"):
            if value.startswith(("http://", "https://", "#", "javascript:", "mailto:", "data:", "${")):
                continue
            refs.add(value.split("?")[0])

    assert refs, "expected local asset references in index.html"
    for ref in refs:
        assert (ROOT / ref).exists(), f"missing local asset referenced by index.html: {ref}"


def test_inline_onclick_handlers_are_defined():
    defined = set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", HTML))
    called = set()
    for handler in re.findall(r'on\w+="([^"]*)"', HTML):
        called.update(re.findall(r"([A-Za-z_$][\w$]*)\s*\(", handler))

    builtins = {"stopPropagation", "if", "return"}
    missing = sorted(called - defined - builtins)
    assert not missing, f"inline handlers reference undefined functions: {missing}"
