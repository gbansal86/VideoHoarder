from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")
URL_RE = re.compile(r"(?:(?:https?:)?//|www\.)[^\s\]\)]+", re.I)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((https?://[^\s\)]+)\)", re.I)
TS_ANY_RE = re.compile(r"(?<!\d)(\d{1,2}:\d{2}(?::\d{2})?)(?!\d)")

OPTION_RE = re.compile(r"(?i)\(\s*option\s*(\d+)\s*\)")
PRICE_RE = re.compile(r"(?i)\(\s*rs\.?\s*[^)]*\)")
DISCOUNT_CODE_RE = re.compile(
    r"(?i)\b(?:apply|use)\s+(?:discount\s+)?(?:code|coupon(?:\s+code)?)\s*[-:–—]?\s*([A-Z0-9_-]+)"
)
DISCOUNT_PERCENT_RE = re.compile(r"(?i)\b(\d{1,2})\s*%\s*off\b")
DISCOUNT_RUPEES_RE = re.compile(r"(?i)\b(?:rs\.?|₹)\s*([0-9][0-9,]*)\s*(?:off|discount)\b")
NOT_SPONSORED_RE = re.compile(r"(?i)\bnot\s+sponsored\b")
SPONSORED_RE = re.compile(r"(?i)\bsponsored\b")
PARTNER_RE = re.compile(r"(?i)\b(?:video|segment)\s+partner\b")
BUY_RE = re.compile(r"(?i)^\s*buy\b")

# These patterns map creator headings to normalized categories while retaining
# the exact original heading in output. Order matters: more specific first.
SECTION_RULES = [
    ("related_products", re.compile(
        r"(?i)^\s*(?:foods?\s*(?:&|and)\s*)?products?\s+related\s+to\s+(?:the|this)?\s*video\b.*$"
        r"|^\s*you may (?:need|want to buy)\b.*$"
        r"|^\s*make\s+.+\s+you may need\b.*$"
        r"|^\s*(?:below are the links to the exact )?ingredients(?:\s+used\s+in\s+.+)?\s*:?[\s📦]*$"
        r"|^\s*buy\s+.+\s+products?\b.*$"
        r"|^\s*buy\s+best\s+.+\s+in\s+(?:the\s+)?indian market\b.*$"
        r"|^\s*(?:best|natural|healthier|ayurvedic|handpicked)\s+.+\s+(?:as\s+)?(?:mentioned|listed|suggested|related)\s+(?:in|to)\s+(?:the|this)\s+video\b.*$"
    )),
    ("recommended_videos", re.compile(
        r"(?i)^\s*recommended videos?\b.*$"
        r"|^\s*related videos?(?:\s+for more recipes|\s+to cure [^\n]+)?\b.*$"
        r"|^\s*more on\s+fit\s+tuber\b.*$"
        r"|^\s*more on\s+[^.!?]{1,60}:?\s*$"
        r"|^\s*some of my most popular videos\b.*$"
        r"|^\s*(?:📹\s*)?videos(?:\s*📹)?\s*$"
    )),
    ("video_recommendations", re.compile(
        r"(?i)^\s*best\s+.+\s+in\s+(?:the\s+)?indian market\b.*$"
    )),
    ("generic_products", re.compile(
        r"(?i)^\s*best products? from\b.*$"
        r"|^\s*worst to best series\b.*$"
    )),
    ("seasonal_products", re.compile(
        r"(?i)^\s*(?:winter|summer|monsoon)\s+products?\b.*$"
    )),
    ("books", re.compile(
        r"(?i)^\s*(?:📚\s*)?books(?:\s*📚)?\s*$"
        r"|^\s*(?:some\s+)?book recommendations?\b.*$"
        r"|^\s*my favou?rite books\b.*$"
    )),
    ("music", re.compile(
        r"(?i)^\s*(?:🎵\s*)?music(?:\s*🎵)?\s*$"
        r"|^\s*instrumental music\b.*$"
    )),
    ("gear", re.compile(r"(?i)^\s*my gear\b.*$")),
    ("useful_links", re.compile(r"(?i)^\s*(?:(?:some|more)\s+)?useful links\b.*$")),
    ("instagram", re.compile(r"(?i)^\s*instagram\b.*$")),
    ("support", re.compile(
        r"(?i)^\s*(?:✅\s*)?(?:support my work\b|if you want to support this work\b).*$"
    )),
    ("disclaimer", re.compile(r"(?i)^\s*disclaimer\b.*$")),
    ("music_credits", re.compile(r"(?i)^\s*music credits?\b.*$")),
]

GENERIC_HEADING_WORDS = {
    "products", "recommendations", "recommended", "links", "gear", "videos",
    "ingredients", "resources", "social", "follow", "support", "credits"
}


def clean_line(value: str) -> str:
    value = ZERO_WIDTH_RE.sub("", value).strip()
    return re.sub(r"\s+", " ", value)


def timestamp_to_seconds(timestamp: str) -> int:
    parts = [int(x) for x in timestamp.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


# Backward-compatible alias.
ts_seconds = timestamp_to_seconds


def extract_links(line: str) -> list[dict]:
    """Extract unique links from one source line.

    Markdown links are recognized before bare URLs so that
    [https://x](https://x) is stored once rather than twice.
    """
    found = []
    seen = set()
    spans = []

    for match in MD_LINK_RE.finditer(line):
        url = match.group(2).rstrip(".,;:")
        if url not in seen:
            found.append({
                "url": url,
                "normalized_url": normalize_url(url),
                "label": clean_line(match.group(1)),
                "markdown": True,
            })
            seen.add(url)
        spans.append(match.span())

    masked = line
    if spans:
        chars = list(line)
        for start, end in spans:
            chars[start:end] = " " * (end - start)
        masked = "".join(chars)

    for match in URL_RE.finditer(masked):
        url = match.group(0).rstrip(".,;:")
        if url not in seen:
            found.append({"url": url, "normalized_url": normalize_url(url), "label": "", "markdown": False})
            seen.add(url)

    return found


def strip_links_from_line(line: str) -> str:
    """Remove link syntax while retaining a useful Markdown label."""
    def repl(match):
        label = clean_line(match.group(1))
        if label.lower().startswith(("http://", "https://")):
            return ""
        return label

    result = MD_LINK_RE.sub(repl, line)
    result = URL_RE.sub("", result)
    result = re.sub(r"\s+", " ", result)
    return result.strip(" -–—:[]")


def normalize_url(url: str) -> str:
    value = url.strip()
    if value.startswith("//"):
        return "https:" + value
    if value.lower().startswith("www."):
        return "https://" + value
    return value

def classify_url(url: str) -> str:
    try:
        domain = urlparse(normalize_url(url)).netloc.lower().removeprefix("www.")
    except Exception:
        return "other"
    if domain == "amzn.to" or "amazon." in domain or domain == "link.amazon":
        return "amazon"
    if "youtube.com" in domain or domain == "youtu.be":
        return "youtube"
    if "instagram.com" in domain:
        return "instagram"
    return "other"


def _looks_like_custom_heading(line: str) -> bool:
    """Very conservative fallback for unknown structural headings.

    A title-cased sentence such as a recommended video title must never become a
    section merely because it contains words like "products" or "follow".
    """
    if TS_ANY_RE.search(line) or extract_links(line) or len(line) > 90:
        return False

    letters = [c for c in line if c.isalpha()]
    words = re.findall(r"[A-Za-z]+", line.lower())
    if not letters or not words:
        return False

    uppercase_ratio = sum(c.isupper() for c in letters) / len(letters)
    has_heading_word = any(word in GENERIC_HEADING_WORDS for word in words)
    return (
        uppercase_ratio >= 0.90
        and has_heading_word
        and len(words) <= 8
        and not line.endswith((".", "?", "!"))
    )



def split_section_header(line: str, category: str):
    """Return a concise semantic header plus inline source content when appropriate."""
    original = clean_line(line)
    if category == "disclaimer":
        m = re.match(r"(?i)^\s*disclaimer\s*[:\-–—]?\s*(.*)$", original)
        if m:
            return "DISCLAIMER", clean_line(m.group(1)) or None
    if category == "instagram":
        m = re.match(r"(?i)^\s*instagram\s*[:\-–—]?\s*(.*)$", original)
        if m:
            return "INSTAGRAM", clean_line(m.group(1)) or None
    return original, None

def detect_section(line: str):
    """Return normalized category for a structural header, else None."""
    if TS_ANY_RE.search(line):
        return None
    for name, rx in SECTION_RULES:
        if rx.match(line):
            # Product purchase lines commonly contain words that resemble a
            # heading ("Buy X Products...") but are item rows. Inline links are
            # structural only for support/social headers.
            if extract_links(line) and name not in {"support", "instagram"}:
                return None
            return name
    if _looks_like_custom_heading(line):
        return "custom"
    return None


def normalize_product(name: str):
    option = None
    match = OPTION_RE.search(name)
    if match:
        option = int(match.group(1))
    value = OPTION_RE.sub("", name)
    value = PRICE_RE.sub("", value)
    value = re.sub(r"\s+", " ", value).strip(" -–—")
    return value, option


def parse_promotion_attributes(text: str) -> dict:
    code = None
    percent = None
    code_match = DISCOUNT_CODE_RE.search(text)
    if code_match:
        code = code_match.group(1)
    pct_match = DISCOUNT_PERCENT_RE.search(text)
    if pct_match:
        percent = int(pct_match.group(1))

    amount_rupees = None
    rs_match = DISCOUNT_RUPEES_RE.search(text)
    if rs_match:
        amount_rupees = int(rs_match.group(1).replace(",", ""))

    not_sponsored = bool(NOT_SPONSORED_RE.search(text))
    sponsored = bool(SPONSORED_RE.search(text)) and not not_sponsored

    return {
        "discount_code": code,
        "discount_percent": percent,
        "discount_amount_rupees": amount_rupees,
        "not_sponsored": not_sponsored,
        "sponsored": sponsored,
        "partner_mention": bool(PARTNER_RE.search(text)),
    }


def _clean_item_label(text: str) -> str:
    value = strip_links_from_line(text)
    value = re.sub(r"(?i)^\s*buy\s+", "", value)
    # Keep sponsorship wording in original_text/attributes, but remove it from the label.
    value = re.sub(r"(?i)\(?\s*not sponsored\s*\)?", "", value)
    value = re.sub(r"(?i)\(?\s*sponsored\s*\)?", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" -–—:")


def _is_probable_title_line(line: str) -> bool:
    if not line or extract_links(line) or TS_ANY_RE.search(line):
        return False
    if _looks_like_call_to_action(line):
        return False
    if detect_section(line):
        return False
    if DISCOUNT_CODE_RE.search(line) or DISCOUNT_PERCENT_RE.search(line):
        return False
    if len(line) > 180:
        return False
    # Prose sentences are poor link titles; short labels/titles are useful.
    return not (len(line) > 100 and line.endswith("."))



OUTLINE_PREFIX_RE = re.compile(
    r"(?i)^\s*(?:"
    r"(?:diet\s+)?myth\s*#?\s*\d+"
    r"|#?\s*\d+\s*[-.:)]"
    r"|(?:step|tip|hack|habit|mistake|food|way|remedy)\s*#?\s*\d+"
    r")\b"
)

CTA_RE = re.compile(
    r"(?i)^\s*(?:"
    r"like\s*(?:\||/|,|\s)+\s*share(?:\s*(?:\||/|,|\s)+\s*comment)?"
    r"|subscribe\s*:?"
    r"|follow\s+me"
    r")\s*$"
)

def _looks_like_call_to_action(line: str) -> bool:
    return bool(CTA_RE.match(clean_line(line)))

def _looks_like_outline_item(line: str) -> bool:
    """Identify useful list/step lines that are content, not section headings."""
    if not line or extract_links(line) or TS_ANY_RE.search(line):
        return False
    if detect_section(line):
        return False
    if OUTLINE_PREFIX_RE.search(line):
        return True

    # Short all-caps phrases are commonly workout steps / recipe stages.
    letters = [c for c in line if c.isalpha()]
    if not letters:
        return False
    uppercase_ratio = sum(c.isupper() for c in letters) / len(letters)
    words = re.findall(r"[A-Za-z]+", line)
    return uppercase_ratio >= 0.90 and 1 <= len(words) <= 8 and len(line) <= 90


PURCHASE_QUALIFIER_RE = re.compile(
    r"(?i)\s*\((?:amazon|flipkart|website|alternate link)\)\s*$"
)

def _base_purchase_label(label: str) -> str:
    """Remove parser-added store qualifiers to recover the clean product name."""
    value = clean_line(label)
    while PURCHASE_QUALIFIER_RE.search(value):
        value = PURCHASE_QUALIFIER_RE.sub("", value).strip()
    return value

def _is_generic_purchase_label(label: str) -> bool:
    x = clean_line(label).lower().strip(" -:()")
    return x in {
        "from amazon", "amazon", "buy from amazon",
        "flipkart", "from flipkart", "buy from flipkart",
        "website link", "website", "buy here", "buy online"
    } or x.startswith("from amazon ") or x.startswith("from flipkart ")


CONTEXT_CUE_RE = re.compile(
    r"(?i)\b(?:"
    r"watch (?:this|these|the)(?:\s+(?:one|two|three|four|five|\d+))?\s+(?:video|videos)"
    r"|checkout (?:this|the) video"
    r"|check out (?:this|the) video"
    r"|click (?:the )?link(?: below)?"
    r"|link below"
    r"|video sponsor"
    r"|video partner"
    r"|segment partner"
    r"|donate|donation"
    r"|website"
    r"|subscribe"
    r"|follow me"
    r"|recommendation"
    r")\b"
)

def _context_candidate(line: str, chapter_text: str | None = None) -> str | None:
    """Return explicit nearby source text that can safely contextualize a bare URL."""
    if chapter_text and chapter_text.strip():
        # Timestamp lines frequently introduce a sponsor/partner URL on the next line.
        if CONTEXT_CUE_RE.search(chapter_text):
            return clean_line(chapter_text)
    if CONTEXT_CUE_RE.search(line):
        return clean_line(line)
    return None

def _display_context_label(context: str) -> str:
    """Keep source wording as the label; only trim bullets/punctuation."""
    x = clean_line(context)
    x = re.sub(r"^\s*[-•]\s*", "", x)
    return x.strip(" -–—:")


def build_duplicate_url_groups(url_records: list[dict]) -> list[dict]:
    """Summarize repeated normalized URLs without removing any occurrence."""
    groups = {}
    for rec in url_records:
        key = rec.get("normalized_url") or rec.get("url")
        groups.setdefault(key, []).append(rec)

    duplicate_groups = []
    for key, records in groups.items():
        if len(records) < 2:
            continue
        duplicate_groups.append({
            "normalized_url": key,
            "occurrence_count": len(records),
            "occurrences": [
                {
                    "url": r.get("url"),
                    "line": r.get("line"),
                    "section": r.get("section"),
                    "original_text": r.get("original_text"),
                }
                for r in records
            ],
        })
    return duplicate_groups

def parse_description(text: str, boilerplate_lines: set[str] | None = None) -> dict:
    raw_lines = text.splitlines()
    source_lines = []
    for raw_index, raw in enumerate(raw_lines, 1):
        cleaned = clean_line(raw)
        if cleaned:
            source_lines.append({
                "source_line": raw_index,
                "text": cleaned,
                "raw": raw,
            })

    title = source_lines[0]["text"] if source_lines else ""

    sections = []
    section_blocks = [{
        "id": 0,
        "category": "preamble",
        "header": None,
        "header_original": None,
        "header_content": None,
        "header_line": None,
        "items": [],
        "content_lines": [],
    }]
    current_block = section_blocks[0]

    chapters = []
    urls = []
    link_items = []
    promotions = []
    introduction = []
    boilerplate_matches = []

    pending_label = None
    pending_label_line = None
    active_context_label = None
    active_context_line = None
    active_context_uses = 0
    last_specific_purchase_label = None
    last_specific_purchase_line = None
    outline_items = []
    calls_to_action = []

    for logical_index, entry in enumerate(source_lines, 1):
        line = entry["text"]
        source_line = entry["source_line"]

        # The first non-empty line is the video title. Never reinterpret it as
        # a structural section heading, even when it is short/all-caps.
        sec = None if logical_index == 1 else detect_section(line)

        # Context-aware fallback: a short all-caps line immediately followed by
        # one or more links is almost certainly a creator section heading, not a
        # workout/list item. This recovers rare headings without reintroducing
        # the V4 over-classification problem.
        if logical_index != 1 and sec is None and not _looks_like_call_to_action(line):
            letters = [c for c in line if c.isalpha()]
            if letters and len(line) <= 90:
                upper_ratio = sum(c.isupper() for c in letters) / len(letters)
                if upper_ratio >= 0.90:
                    # Inspect the next three non-empty source lines.
                    pos = logical_index - 1
                    future = source_lines[pos + 1:pos + 4]
                    if any(extract_links(x["text"]) for x in future):
                        sec = "custom"

        if sec:
            semantic_header, inline_header_content = split_section_header(line, sec)
            current_block = {
                "id": len(section_blocks),
                "category": sec,
                "header": semantic_header,
                "header_original": line,
                "header_content": inline_header_content,
                "header_line": source_line,
                "items": [],
                "content_lines": [],
            }
            section_blocks.append(current_block)
            sections.append({
                "id": current_block["id"],
                "line": source_line,
                "name": sec,
                "category": sec,
                "header": semantic_header,
                "header_original": line,
                "header_content": inline_header_content,
            })
            # If a structural heading is followed by a bare URL, the heading
            # itself is useful label context (SUPPORT, INSTAGRAM, etc.).
            pending_label = semantic_header
            pending_label_line = source_line
            if inline_header_content:
                current_block["content_lines"].append({
                    "line": source_line,
                    "text": inline_header_content,
                    "from_inline_header": True,
                })
            # A heading can itself contain a link in unusual descriptions.
            # Do not continue; link extraction below must still run.

        section_category = current_block["category"]
        section_header = current_block["header"]

        line_links = extract_links(line)

        # Timestamp/chapter extraction is independent of section parsing.
        current_chapter_text = None
        for match in TS_ANY_RE.finditer(line):
            ts = match.group(1)
            before = line[:match.start()].strip(" -–—:.")
            after = line[match.end():].strip(" -–—:.")
            chapter_text = after if after else before
            if before and after:
                chapter_text = f"{before} - {after}".strip(" -")
            current_chapter_text = chapter_text
            chapters.append({
                "timestamp": ts,
                "seconds": timestamp_to_seconds(ts),
                "text": chapter_text,
                "line": source_line,
                "section": section_category,
            })

        attrs = parse_promotion_attributes(line)
        if any(attrs.values()):
            promotions.append({
                "line": source_line,
                "text": line,
                "section": section_category,
                "section_header": section_header,
                **attrs,
            })

        # Preserve every URL occurrence with local semantic context.
        for link in line_links:
            urls.append({
                "url": link["url"],
                "normalized_url": link.get("normalized_url", normalize_url(link["url"])),
                "type": classify_url(link["url"]),
                "line": source_line,
                "original_text": line,
                "label": link["label"],
                "markdown": link["markdown"],
                "section": section_category,
                "section_header": section_header,
                "section_id": current_block["id"],
                "is_boilerplate_section": section_category in {
                    "generic_products", "support", "instagram", "gear",
                    "music_credits", "music"
                },
            })

        # Explicit nearby source context can label otherwise bare links.
        new_context = _context_candidate(line, current_chapter_text)
        if new_context and not line_links:
            active_context_label = new_context
            active_context_line = source_line
            active_context_uses = 0

        # Associate a URL with useful text from the same line, or from the
        # immediately preceding unlinked title/label line.
        if line_links:
            same_line_label = _clean_item_label(line)
            label_source = "same_line"
            label_line = source_line

            if not same_line_label or same_line_label.lower().startswith(("http://", "https://")):
                same_line_label = ""
                label_source = None

            # Markdown display text may itself be the useful item name.
            if not same_line_label:
                markdown_label = next(
                    (clean_line(x["label"]) for x in line_links
                     if x["label"] and not x["label"].lower().startswith(("http://", "https://"))),
                    "",
                )
                if markdown_label:
                    same_line_label = markdown_label
                    label_source = "markdown_label"

            if not same_line_label and pending_label:
                same_line_label = pending_label
                label_source = "previous_line"
                label_line = pending_label_line

            # If a bare URL follows explicit source wording such as "watch these
            # two videos", "video sponsor", or "click the link below", retain
            # that wording as deterministic context. The same context may label
            # consecutive bare URLs.
            if not same_line_label and active_context_label and active_context_uses < 4:
                same_line_label = _display_context_label(active_context_label)
                label_source = "nearby_context"
                label_line = active_context_line
                active_context_uses += 1

            if (
                same_line_label
                and same_line_label.strip().lower() in {"link", "website link", "click here"}
                and active_context_label
            ):
                same_line_label = _display_context_label(active_context_label)
                label_source = "nearby_context"
                label_line = active_context_line
                active_context_uses += 1

            # Store-only labels such as "Amazon - URL", "Flipkart - URL", and
            # "Website - URL" often belong to the product named on the immediately
            # preceding line (e.g. "Buy Sunova Bioslim"). Prefer that explicit
            # nearby product name before falling back to earlier product context.
            generic_purchase_label = same_line_label
            if (
                same_line_label
                and _is_generic_purchase_label(same_line_label)
                and pending_label
                and not _is_generic_purchase_label(pending_label)
            ):
                inherited = re.sub(r"(?i)^\s*buy\s+", "", pending_label).strip()
                inherited = _base_purchase_label(inherited)
                primary_type = classify_url(line_links[0]["url"])
                lower = generic_purchase_label.lower()
                if "amazon" in lower or primary_type == "amazon":
                    qualifier = "Amazon"
                elif "flipkart" in lower:
                    qualifier = "Flipkart"
                elif "website" in lower:
                    qualifier = "Website"
                else:
                    qualifier = "Alternate link"
                same_line_label = f"{inherited} ({qualifier})"
                label_source = "previous_line_product_context"
                label_line = pending_label_line

            if same_line_label and _is_generic_purchase_label(same_line_label) and last_specific_purchase_label:
                primary_type = classify_url(line_links[0]["url"])
                generic_lower = generic_purchase_label.lower()
                if "amazon" in generic_lower or primary_type == "amazon":
                    qualifier = "Amazon"
                elif "flipkart" in generic_lower:
                    qualifier = "Flipkart"
                elif "website" in generic_lower:
                    qualifier = "Website"
                else:
                    qualifier = "Alternate link"
                base_product = _base_purchase_label(last_specific_purchase_label)
                same_line_label = f"{base_product} ({qualifier})"
                label_source = "previous_product_context"
                label_line = last_specific_purchase_line

            item_attrs = parse_promotion_attributes(line)
            item = {
                "label": same_line_label,
                "urls": [x["url"] for x in line_links],
                "normalized_urls": [x.get("normalized_url", normalize_url(x["url"])) for x in line_links],
                "url_types": [classify_url(x["url"]) for x in line_links],
                "primary_url": line_links[0]["url"],
                "line": source_line,
                "label_line": label_line,
                "label_source": label_source,
                "context_text": active_context_label if label_source == "nearby_context" else None,
                "context_line": active_context_line if label_source == "nearby_context" else None,
                "original_text": line,
                "section": section_category,
                "section_header": section_header,
                "section_id": current_block["id"],
                "preserved": True,
                **item_attrs,
            }
            link_items.append(item)
            current_block["items"].append(item)

            if item["label"] and not _is_generic_purchase_label(item["label"]):
                # "Website Link" is generic and shouldn't replace a real product.
                if item["label"].lower() not in {"website link", "website"}:
                    last_specific_purchase_label = _base_purchase_label(item["label"])
                    last_specific_purchase_line = item["label_line"]

            # A URL consumes the immediately preceding pending label.
            pending_label = None
            pending_label_line = None
        else:
            # Non-header content stays visible inside its creator-defined section.
            if not sec:
                current_block["content_lines"].append({
                    "line": source_line,
                    "text": line,
                })
                if line != title and _looks_like_call_to_action(line):
                    calls_to_action.append({
                        "line": source_line,
                        "text": line,
                        "section": section_category,
                        "section_header": section_header,
                    })
                elif line != title and _looks_like_outline_item(line):
                    outline_items.append({
                        "line": source_line,
                        "text": line,
                        "section": section_category,
                        "section_header": section_header,
                    })

            # A new unrelated non-link line ends a prior contextual-link group.
            if (
                active_context_label
                and source_line != active_context_line
                and not _context_candidate(line, current_chapter_text)
                and not _looks_like_call_to_action(line)
                and not sec
            ):
                # Keep context through short generic discount/instruction lines,
                # otherwise end it to avoid leaking labels into later links.
                if not (
                    DISCOUNT_CODE_RE.search(line)
                    or DISCOUNT_PERCENT_RE.search(line)
                    or DISCOUNT_RUPEES_RE.search(line)
                ):
                    active_context_label = None
                    active_context_line = None
                    active_context_uses = 0

            if _looks_like_call_to_action(line):
                # CTA headings such as SUBSCRIBE/FOLLOW often directly precede
                # their channel/social URL and should label that URL.
                pending_label = line
                pending_label_line = source_line
            elif _is_probable_title_line(line) and line != title:
                pending_label = line
                pending_label_line = source_line
            else:
                # Discount lines should not become future link titles.
                if (
                    DISCOUNT_CODE_RE.search(line)
                    or DISCOUNT_PERCENT_RE.search(line)
                    or DISCOUNT_RUPEES_RE.search(line)
                ):
                    pending_label = None
                    pending_label_line = None

        if boilerplate_lines:
            normalized = normalize_for_frequency(line)
            if normalized in boilerplate_lines:
                boilerplate_matches.append(line)

    # Build backwards-compatible product list from item records in product-like sections.
    product_sections = {
        "related_products", "video_recommendations", "generic_products", "seasonal_products",
        "useful_links", "books",
    }
    products = []
    for item in link_items:
        if item["section"] not in product_sections or not item["label"]:
            continue
        canonical, option = normalize_product(item["label"])
        products.append({
            "name": item["label"],
            "canonical_name": canonical,
            "option": option,
            "url": item["primary_url"],
            "urls": item["urls"],
            "section": item["section"],
            "section_header": item["section_header"],
            "original_text": item["original_text"],
            "line": item["line"],
            "preserved": True,
            "not_sponsored": item["not_sponsored"],
            "sponsored": item["sponsored"],
        })

    # Explicitly identify related/recommended video link items.
    recommended_videos = []
    for item in link_items:
        if item["section"] != "recommended_videos":
            continue
        youtube_urls = [
            u for u, t in zip(item["urls"], item["url_types"]) if t == "youtube"
        ]
        if youtube_urls:
            recommended_videos.append({
                "title": item["label"],
                "urls": youtube_urls,
                "primary_url": youtube_urls[0],
                "line": item["line"],
                "section_header": item["section_header"],
                "original_text": item["original_text"],
            })

    # Preamble introduction: retain meaningful prose, exclude title, links,
    # timestamps, promotional instructions, and tiny item labels.
    preamble_block = section_blocks[0]
    for entry in preamble_block["content_lines"]:
        line = entry["text"]
        if line == title:
            continue
        if extract_links(line) or TS_ANY_RE.search(line):
            continue
        if any(parse_promotion_attributes(line).values()):
            continue
        if _looks_like_outline_item(line) or _looks_like_call_to_action(line):
            continue
        if len(line) < 80:
            continue
        introduction.append(line)

    generic_chapter = re.compile(
        r"(?i)^#?\s*\d+\s*(?:food|way|tip|habit|remedy|mistake)\b"
    )
    descriptive_count = sum(
        bool(c["text"]) and not generic_chapter.search(c["text"]) for c in chapters
    )
    information_level = 0
    if chapters:
        information_level = 1
    if descriptive_count >= max(1, len(chapters) // 2):
        information_level = 2
    if products and information_level >= 2:
        information_level = 3

    return {
        "title": title,
        "introduction": introduction,
        "chapters": chapters,
        "outline_items": outline_items,
        "calls_to_action": calls_to_action,
        "sections": sections,
        "section_blocks": section_blocks,
        "link_items": link_items,
        "products": products,
        "recommended_videos": recommended_videos,
        "promotions": promotions,
        "urls": urls,
        "boilerplate_matches": boilerplate_matches,
        "duplicate_url_groups": build_duplicate_url_groups(urls),
        "metadata": {
            "has_chapters": bool(chapters),
            "chapter_count": len(chapters),
            "has_related_products": any(
                p["section"] == "related_products" for p in products
            ),
            "has_generic_product_catalogue": any(
                p["section"] == "generic_products" for p in products
            ),
            "has_promotional_wording": bool(promotions),
            "url_count": len(urls),
            "link_item_count": len(link_items),
            "recommended_video_count": len(recommended_videos),
            "section_count": len(sections),
            "outline_item_count": len(outline_items),
            "call_to_action_count": len(calls_to_action),
            "description_information_level": information_level,
            "lossless_policy": "raw source retained; links and section context preserved",
        },
    }


def normalize_for_frequency(line: str) -> str:
    value = clean_line(line).lower()
    value = MD_LINK_RE.sub("<url>", value)
    value = URL_RE.sub("<url>", value)
    value = OPTION_RE.sub("(option)", value)
    value = PRICE_RE.sub("(price)", value)
    return re.sub(r"\s+", " ", value).strip()


def learn_boilerplate(texts: list[str], min_files: int = 25):
    counts = Counter()
    for text in texts:
        seen = {
            normalize_for_frequency(x)
            for x in text.splitlines()
            if clean_line(x)
        }
        counts.update(seen)
    return {line for line, count in counts.items() if count >= min_files}, counts


def main():
    parser = argparse.ArgumentParser(
        description="Lossless deterministic YouTube-description parser."
    )
    parser.add_argument("input", help="Description .txt file or directory")
    parser.add_argument("-o", "--output", help="Output JSON path")
    args = parser.parse_args()

    path = Path(args.input)
    if path.is_dir():
        files = sorted(path.rglob("*.txt"))
        texts = [f.read_text(encoding="utf-8", errors="ignore") for f in files]
        boilerplate, _ = learn_boilerplate(texts)
        output = {
            str(f.relative_to(path)): parse_description(text, boilerplate)
            for f, text in zip(files, texts)
        }
    else:
        output = parse_description(
            path.read_text(encoding="utf-8", errors="ignore")
        )

    rendered = json.dumps(output, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
