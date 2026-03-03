#!/usr/bin/env python3
"""
WordPress to Hugo migration script for platypus1917.org

Fetches content via the WP REST API, transforms HTML to Markdown,
simplifies taxonomy, and writes Hugo content files.

Usage:
    # Fetch all raw data from WP REST API
    python migrate.py fetch

    # Transform fetched data into Hugo content files
    python migrate.py transform

    # Do both
    python migrate.py all
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml
from markdownify import markdownify as md

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WP_BASE = "https://platypus1917.org"
WP_API = f"{WP_BASE}/wp-json/wp/v2"

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "data" / "raw"
HUGO_ROOT = SCRIPT_DIR.parent
CONTENT_DIR = HUGO_ROOT / "content"
REDIRECTS_FILE = HUGO_ROOT / "static" / "_redirects"

# Rate limiting
REQUEST_DELAY = 0.25  # seconds between API requests

# Categories whose names match these patterns are PR issue numbers
ISSUE_PATTERN = re.compile(
    r"^(?:The Platypus Review\s*)?#?\s*(\d+)$|"
    r"^PR\s*#?\s*(\d+)$|"
    r"^Issue\s*#?\s*(\d+)$|"
    r"^Platypus Review\s*#?\s*(\d+)$|"
    r"^Ausgabe\s*#?\s*(\d+)$",
    re.IGNORECASE,
)

# Categories that are clearly author names (under "Platypus Review Authors" parent)
# We'll detect these by parent category ID during processing

# Content type categories -> front matter `content_type` field
CONTENT_TYPE_NAMES = {
    "article", "interview", "transcript", "translation", "review",
    "transcripted material",
}

# Location/chapter names and universities — these are structural, not topics
LOCATION_NAMES = {
    "aarhus", "amherst", "athens", "austin", "bay area", "berlin", "bielefeld",
    "bloomington", "boston", "bremen", "cambridge", "chicago", "cincinnati",
    "cologne", "columbia", "corvallis", "dalhousie", "dartmouth", "dc", "detroit",
    "fairfax", "farnham", "frankfurt", "georgetown", "goldsmiths", "greece",
    "halifax", "hamburg", "houston", "jakarta", "jena", "king's university",
    "knoxville", "leipzig", "london", "los angeles", "loyola", "lse",
    "madison", "magdeburg", "manchester", "melbourne", "montreal", "nashville",
    "new haven", "new school", "new york", "northwestern", "nyu", "oxford",
    "paris", "philadelphia", "pittsburgh", "prishtina", "rochester",
    "saic", "san francisco", "santa cruz", "seoul", "sheffield", "stony brook",
    "sva", "switzerland", "thessaloniki", "tokyo", "toronto", "ucl",
    "uchicago", "uic", "vienna", "washington", "zurich", "australia", "germany",
}

# Structural/meta categories to skip entirely
SKIP_CATEGORY_NAMES = {
    "uncategorized",
    # Featured/editorial
    "featured", "featured articles", "featured interviews", "featured media",
    "featured transcripts",
    # Current/latest issue markers
    "current issue", "latest issue of the platypus review",
    "latest issue of the platypus review (german)",
    # Navigation/redirects
    "redirect",
    # Meta groupings
    "platypus review article type", "platypus review topics",
    "the platypus review",
    # Generic media container (specific audio/video handled separately)
    "media", "panels", "panel discussions media", "interviews media",
    # Reading group structural
    "reading groups", "introductory reading groups", "reading group notes",
    "summer reading groups", "primary marxist reading group",
    "german reading groups", "greek reading groups",
    # Announcements (structural)
    "announcements", "international announcements",
    "upcoming international fora",
    # Language/locale markers (handled separately)
    "about platypus", "about platypus (deutsch)", "about platypus (kosovo)",
    "die platypus review",
    "german texts and translations", "greek texts and translations",
    "german decline of the left", "greek decline of the left",
    "greek translation discards", "greek platypus synthesis",
    "the platypus synthesis",
    # Misc structural
    "radical minds",
    "editorial statement of purpose and submission guidelines",
    # PR-prefixed subtopics (duplicates or too granular)
    "pr #occupy", "pr art and culture", "pr lenin", "pr media",
    'pr the student "left"', "pr-iran",
    # Person name miscategorized as topic
    "rick ayers",
    # Podcast section marker
    "shit platypus says",
    # Parent grouping categories (not real topics)
    "international series",
    # Event type markers (use section routing instead)
    "european conference", "left forum",
    "platypus international convention", "teach-ins",
}

# Media type categories -> front matter `media_type` field
MEDIA_TYPE_NAMES = {
    "media audio": "audio",
    "media video": "video",
    "panels audio": "audio",
    "panels video": "video",
}

# Map sub-locations (universities, venues) to their parent city
# If a location is in this map, it gets stored as sublocation with the city as location
SUBLOCATION_TO_CITY = {
    # Chicago
    "saic": "Chicago",
    "uic": "Chicago",
    "uchicago": "Chicago",
    "loyola": "Chicago",
    "northwestern": "Chicago",
    # New York
    "nyu": "New York",
    "columbia": "New York",
    "new school": "New York",
    "sva": "New York",
    "stony brook": "New York",
    # London
    "goldsmiths": "London",
    "lse": "London",
    "ucl": "London",
    "king's university": "London",
    # Other university-based
    "dalhousie": "Halifax",
    "dartmouth": "New Haven",
    "georgetown": "Washington",
    "oxford": "Oxford",
    "cambridge": "Cambridge",
    # Countries -> drop to avoid over-broad locations
    "australia": None,
    "germany": None,
    "greece": None,
    "switzerland": None,
}

# Convention/event year categories -> just use the event date, not a category
CONVENTION_PATTERN = re.compile(
    r"^(?:Platypus International Convention|European Conference|Left Forum)\s*\d{4}$",
    re.IGNORECASE,
)

# German-related category slugs/names
GERMAN_INDICATORS = {
    "die-platypus-review",
    "deutsch",
    "german",
}

# Greek-related category slugs/names
GREEK_INDICATORS = {
    "greek",
    "greece",
    "athens",
    "thessaloniki",
}

# Albanian-related category slugs/names
# Note: "prishtina" excluded — it appears in multi-city event categories (false positives)
ALBANIAN_INDICATORS = {
    "kosovo",
}

# Slug-based language overrides for one-off translations
# (posts/pages with no language-specific WP category)
SLUG_LANGUAGE_OVERRIDES = {
    # Spanish
    "el-capital-en-la-historia-por-una-filosofia-marxista-de-la-historia-de-la-izquierda": "es",
    "mas-alla-de-la-izquierda-y-la-derecha": "es",
    "declaracion-de-proposito": "es",
    # Portuguese
    "a-esquerda-esta-morta-vida-longa-a-esquerda": "pt",
    # Albanian (Prishtina events with no Kosovo category)
    "coffee-break-prishtina": "sq",
    "ideologjite-radikale-sot-marksizmi-dhe-anarkizmi": "sq",
}

# Page URL patterns for language detection (pages lack WP categories)
GERMAN_PAGE_PREFIXES = [
    "germany/", "hamburg", "jena", "cologne", "bielefeld", "frankfurt",
    "leipzig", "magdeburg", "bremen", "aarhus", "lesekreise",
    "uber-uns", "about-platypus-deutsch", "texte-und-ubersetzungen",
    "vergangene-veranstaltungen", "panel-gruene",
]
GREEK_PAGE_PREFIXES = [
    "greece/", "athens/", "thessaloniki/",
]


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

def fetch_paginated(endpoint, params=None, label="items"):
    """Fetch all pages from a paginated WP REST API endpoint."""
    if params is None:
        params = {}
    params.setdefault("per_page", 100)

    all_items = []
    page = 1

    while True:
        params["page"] = page
        print(f"  Fetching {label} page {page}...", end=" ", flush=True)

        resp = requests.get(f"{WP_API}/{endpoint}", params=params, timeout=30)

        if resp.status_code == 400:
            # WP returns 400 when page exceeds total pages
            print("(no more pages)")
            break

        if resp.status_code == 401:
            print(f"(401 unauthorized — skipping {label})")
            break

        resp.raise_for_status()
        items = resp.json()

        if not items:
            print("(empty)")
            break

        all_items.extend(items)
        total = resp.headers.get("X-WP-Total", "?")
        total_pages = resp.headers.get("X-WP-TotalPages", "?")
        print(f"got {len(items)} (total: {total}, page {page}/{total_pages})")

        if page >= int(resp.headers.get("X-WP-TotalPages", page)):
            break

        page += 1
        time.sleep(REQUEST_DELAY)

    return all_items


def fetch_all():
    """Fetch all content from the WP REST API and save as JSON."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    endpoints = {
        "posts": ("posts", {"status": "publish", "_embed": 1}),
        "pages": ("pages", {"status": "publish", "_embed": 1}),
        "categories": ("categories", {}),
        "tags": ("tags", {}),
        "users": ("users", {}),
        "media": ("media", {}),
    }

    for name, (endpoint, extra_params) in endpoints.items():
        print(f"\n{'='*60}")
        print(f"Fetching {name}...")
        print(f"{'='*60}")

        items = fetch_paginated(endpoint, extra_params, label=name)

        out_path = RAW_DIR / f"{name}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

        print(f"  -> Saved {len(items)} {name} to {out_path}")

    print(f"\nFetch complete. Raw data in {RAW_DIR}")


# ---------------------------------------------------------------------------
# Taxonomy Classification
# ---------------------------------------------------------------------------

def classify_categories(categories):
    """
    Classify WP categories into:
    - issue_numbers: PR issue categories -> front matter `issue` field
    - author_categories: author name categories -> front matter `author` field
    - topic_categories: real topical categories to keep
    - skip: structural/navigation categories to drop
    """
    # Find the parent ID for "Platypus Review Authors" and "Event Speakers"
    author_parent_ids = set()
    speaker_parent_ids = set()

    for cat in categories:
        name_lower = cat["name"].lower()
        if "platypus review authors" in name_lower:
            author_parent_ids.add(cat["id"])
        if "event speakers" in name_lower:
            speaker_parent_ids.add(cat["id"])

    # Also find children-of-children (authors are nested under the parent)
    # WP categories can be nested, so collect all descendants
    def get_descendants(parent_ids, all_cats):
        found = set(parent_ids)
        changed = True
        while changed:
            changed = False
            for c in all_cats:
                if c["parent"] in found and c["id"] not in found:
                    found.add(c["id"])
                    changed = True
        return found - parent_ids  # return only the leaf descendants

    author_cat_ids = get_descendants(author_parent_ids, categories)
    speaker_cat_ids = get_descendants(speaker_parent_ids, categories)

    issue_map = {}          # cat_id -> issue_number (int)
    author_map = {}         # cat_id -> author_name (str)
    speaker_map = {}        # cat_id -> speaker_name (str)
    content_type_map = {}   # cat_id -> content_type (str)
    media_type_map = {}     # cat_id -> "audio" | "video"
    location_map = {}       # cat_id -> location_name (str, city-level only)
    topic_map = {}          # cat_id -> category_name (str)
    skip_ids = set()

    for cat in categories:
        cid = cat["id"]
        name = cat["name"].strip()
        slug = cat["slug"]
        name_lower = name.lower()

        # Skip explicitly listed structural categories
        if name_lower in SKIP_CATEGORY_NAMES:
            skip_ids.add(cid)
            continue

        # Check if it's an issue number (English or German)
        m = ISSUE_PATTERN.match(name)
        if m:
            issue_num = int(next(g for g in m.groups() if g is not None))
            # Reject year-like numbers (2007, 2008, ...) — those are year categories, not issues
            if issue_num < 1900:
                issue_map[cid] = issue_num
                continue

        # Check if it's an author
        if cid in author_cat_ids:
            author_map[cid] = name
            continue

        # Check if it's a speaker
        if cid in speaker_cat_ids:
            speaker_map[cid] = name
            continue

        # Check if it's the parent "Platypus Review Authors" or "Event Speakers" itself
        if cid in author_parent_ids or cid in speaker_parent_ids:
            skip_ids.add(cid)
            continue

        # Check if it's a content type
        if name_lower in CONTENT_TYPE_NAMES:
            content_type_map[cid] = name
            continue

        # Check if it's a media type (audio/video)
        if name_lower in MEDIA_TYPE_NAMES:
            media_type_map[cid] = MEDIA_TYPE_NAMES[name_lower]
            continue

        # Check if it's a convention/event year category
        if CONVENTION_PATTERN.match(name):
            skip_ids.add(cid)
            continue

        # Check if it's a location or location sub-category
        # "Chicago" -> location_map[cid] = "Chicago"
        # "Chicago Media" -> location_map[cid] = "Chicago" (strip suffix)
        is_location = False
        for loc in LOCATION_NAMES:
            if name_lower == loc:
                location_map[cid] = name
                is_location = True
                break
            elif name_lower.startswith(loc + " "):
                # Extract just the city name, title-cased from original
                # e.g. "NYU Media" -> find "nyu" match -> use original name's first word(s)
                city_name = name[:len(loc)]
                location_map[cid] = city_name
                is_location = True
                break
        if is_location:
            continue

        # Year-only categories (e.g. "2007", "2019") — structural, skip
        if re.match(r"^\d{4}$", name):
            skip_ids.add(cid)
            continue

        # Everything remaining is a real topic category
        topic_map[cid] = name

    return {
        "issues": issue_map,
        "authors": author_map,
        "speakers": speaker_map,
        "content_types": content_type_map,
        "media_types": media_type_map,
        "locations": location_map,
        "topics": topic_map,
        "skip": skip_ids,
    }


# ---------------------------------------------------------------------------
# Content Transformation
# ---------------------------------------------------------------------------

def clean_title(raw_title):
    """Clean HTML from a WP rendered title.

    Converts <em>/<i> to *italic*, strips all other HTML tags,
    and decodes common HTML entities.
    """
    title = raw_title
    # Convert italic tags to plain text (YAML titles can't contain markdown)
    title = re.sub(r"<(?:em|i)>(.*?)</(?:em|i)>", r"\1", title)
    # Convert <sup>/<sub> to plain text
    title = re.sub(r"<(?:sup|sub)>(.*?)</(?:sup|sub)>", r"\1", title)
    # Strip any remaining HTML tags
    title = re.sub(r"<[^>]+>", "", title)
    # Decode HTML entities
    title = title.replace("&#8217;", "\u2019").replace("&#8216;", "\u2018")
    title = title.replace("&#8220;", "\u201c").replace("&#8221;", "\u201d")
    title = title.replace("&#8211;", "\u2013").replace("&#8212;", "\u2014")
    title = title.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    title = title.replace("&nbsp;", " ")
    # Collapse whitespace
    title = re.sub(r"\s+", " ", title).strip()
    return title


def html_to_markdown(html_content):
    """Convert HTML content to clean Markdown."""
    if not html_content:
        return ""

    # markdownify handles the heavy lifting
    markdown = md(
        html_content,
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )

    # Clean up excessive whitespace
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)

    # Fix WordPress shortcodes that markdownify wrongly converted to links
    # e.g. [[archiveorg ...]](http://[archiveorg%20...]) → <!-- archiveorg embed -->
    markdown = re.sub(
        r'\[(\[(?:archiveorg|soundcloud|embed|caption)[^\]]*\])\]\([^)]*\)',
        r'<!-- WP shortcode: \1 -->',
        markdown,
    )

    markdown = markdown.strip()

    return markdown


def rewrite_urls(content):
    """Rewrite WordPress URLs in content to Hugo paths."""
    # Rewrite full domain media URLs
    content = content.replace(
        f"{WP_BASE}/wp-content/uploads/",
        "/uploads/"
    )

    # Protocol-relative and http variants
    content = content.replace(
        "//platypus1917.org/wp-content/uploads/",
        "/uploads/"
    )

    # Relative /wp-content/uploads/ paths
    content = content.replace(
        "/wp-content/uploads/",
        "/uploads/"
    )

    return content


def extract_issue_number(category_ids, issue_map):
    """Extract PR issue number from category IDs."""
    for cid in category_ids:
        if cid in issue_map:
            return issue_map[cid]
    return None


def extract_authors(post, category_ids, author_map, user_map):
    """Extract author name(s) from category or user data."""
    # First try: author categories (more specific)
    cat_authors = [author_map[cid] for cid in category_ids if cid in author_map]
    if cat_authors:
        return cat_authors

    # Second try: embedded author data from _embed
    embedded = post.get("_embedded", {})
    embed_authors = embedded.get("author", [])
    if embed_authors and isinstance(embed_authors, list):
        for author in embed_authors:
            if isinstance(author, dict):
                name = author.get("name", "")
                if name and name.lower() not in ("admin", "administrator", "platypus"):
                    return [name]

    # Fallback: WP user map
    author_id = post.get("author")
    if author_id and author_id in user_map:
        name = user_map[author_id]
        if name and name.lower() not in ("admin", "administrator", "platypus"):
            return [name]

    return []


def extract_locations(category_ids, location_map):
    """Extract and decompose locations into city + sublocation.

    Returns (cities, sublocations) where:
    - cities: set of city-level names
    - sublocations: set of specific venue/university names
    """
    cities = set()
    sublocations = set()

    raw_locations = {location_map[cid] for cid in category_ids if cid in location_map}

    for loc in raw_locations:
        loc_lower = loc.lower()
        if loc_lower in SUBLOCATION_TO_CITY:
            city = SUBLOCATION_TO_CITY[loc_lower]
            if city is not None:  # None means "drop" (country-level)
                cities.add(city)
                sublocations.add(loc)
        else:
            # It's already a city-level name
            cities.add(loc)

    return sorted(cities), sorted(sublocations)


def extract_topics(category_ids, topic_map):
    """Extract meaningful topic categories."""
    topics = [topic_map[cid] for cid in category_ids if cid in topic_map]
    # Sanitize: remove chars that produce invalid filenames (#, ?)
    return [t.lstrip("#") for t in topics]


def detect_language(post_or_page, category_ids, categories_raw):
    """Detect content language from categories, title, and slug.

    Returns 'en', 'de', 'el', 'sq', 'es', or 'pt'.
    """
    # Check explicit slug overrides first (one-off translations)
    post_slug = post_or_page.get("slug", "").lower()
    if post_slug in SLUG_LANGUAGE_OVERRIDES:
        return SLUG_LANGUAGE_OVERRIDES[post_slug]

    for cat in categories_raw:
        if cat["id"] in category_ids:
            slug = cat.get("slug", "")
            name = cat.get("name", "").lower()
            # German
            if slug in GERMAN_INDICATORS or any(g in name for g in GERMAN_INDICATORS):
                return "de"
            # Greek
            if slug in GREEK_INDICATORS or any(g in name for g in GREEK_INDICATORS):
                return "el"
            # Albanian
            if slug in ALBANIAN_INDICATORS or any(g in name for g in ALBANIAN_INDICATORS):
                return "sq"

    title = post_or_page.get("title", {}).get("rendered", "")
    if "die platypus review" in title.lower():
        return "de"

    # Check slug for URL-encoded Greek chars (Greek UTF-8 starts with %ce/%cf)
    if "%ce" in post_slug or "%cf" in post_slug:
        return "el"

    return "en"


def detect_page_language(page):
    """Detect page language from URL path and slug (pages lack WP categories)."""
    link = page.get("link", "")
    link_path = link.replace(WP_BASE, "").strip("/").lower()
    slug = page.get("slug", "").lower()

    # Check explicit slug overrides first (one-off translations)
    if slug in SLUG_LANGUAGE_OVERRIDES:
        return SLUG_LANGUAGE_OVERRIDES[slug]

    # Check URL-encoded Greek chars in slug (Greek UTF-8 starts with %ce/%cf)
    if "%ce" in slug or "%cf" in slug:
        return "el"

    for prefix in GERMAN_PAGE_PREFIXES:
        if link_path.startswith(prefix) or link_path == prefix.rstrip("/"):
            return "de"

    for prefix in GREEK_PAGE_PREFIXES:
        if link_path.startswith(prefix) or link_path == prefix.rstrip("/"):
            return "el"

    return "en"


def determine_section(post, category_ids, topic_map):
    """Determine which Hugo section a post belongs to."""
    topics = [topic_map.get(cid, "").lower() for cid in category_ids if cid in topic_map]
    title = post.get("title", {}).get("rendered", "").lower()
    slug = post.get("slug", "").lower()

    # Check for event-related content
    event_keywords = ["convention", "conference", "left forum", "teach-in", "public forum"]
    if any(kw in title or kw in slug for kw in event_keywords):
        return "events"

    # Check for podcast
    if "podcast" in title or "podcast" in slug or "shit platypus says" in title:
        return "podcast"

    # Default: most posts are Platypus Review articles
    return "review"


def get_featured_image(post):
    """Extract featured image URL from embedded data."""
    embedded = post.get("_embedded", {})
    media = embedded.get("wp:featuredmedia", [])
    if media and isinstance(media, list) and len(media) > 0:
        img = media[0]
        if isinstance(img, dict):
            url = img.get("source_url", "")
            if url:
                return url.replace(f"{WP_BASE}/wp-content/uploads/", "/uploads/")
    return None


def transform_post(post, classified, user_map, categories_raw):
    """Transform a single WP post into Hugo front matter + markdown body."""
    title = clean_title(post["title"]["rendered"])

    date = post["date"]
    slug = post["slug"]
    category_ids = post.get("categories", [])
    # Extract structured fields
    issue = extract_issue_number(category_ids, classified["issues"])
    authors = extract_authors(post, category_ids, classified["authors"], user_map)
    topics = extract_topics(category_ids, classified["topics"])
    content_types = [classified["content_types"][cid] for cid in category_ids
                     if cid in classified["content_types"]]
    media_types = list({classified["media_types"][cid] for cid in category_ids
                        if cid in classified["media_types"]})
    cities, sublocations = extract_locations(category_ids, classified["locations"])
    featured_image = get_featured_image(post)
    lang = detect_language(post, category_ids, categories_raw)
    section = determine_section(post, category_ids, classified["topics"])

    # Build front matter
    front_matter = {
        "title": title,
        "date": date,
        "slug": slug,
    }

    if authors:
        front_matter["authors"] = authors
    if issue:
        front_matter["issue"] = issue
    if content_types:
        front_matter["content_type"] = content_types[0].lower()
    if cities:
        front_matter["location"] = cities
    if sublocations:
        front_matter["sublocation"] = sublocations
    if media_types:
        front_matter["media_type"] = media_types[0]
    if topics:
        front_matter["categories"] = topics
    if featured_image:
        front_matter["featured_image"] = featured_image

    # Excerpt
    excerpt = post.get("excerpt", {}).get("rendered", "")
    if excerpt:
        excerpt_text = html_to_markdown(excerpt).strip()
        if excerpt_text and len(excerpt_text) < 500:
            front_matter["excerpt"] = excerpt_text

    # Convert body
    html_content = post.get("content", {}).get("rendered", "")
    body = html_to_markdown(html_content)
    body = rewrite_urls(body)

    # Build old URL for redirect
    try:
        dt = datetime.fromisoformat(date)
        old_path = f"/{dt.year}/{dt.month:02d}/{dt.day:02d}/{slug}/"
    except (ValueError, TypeError):
        old_path = None

    return {
        "front_matter": front_matter,
        "body": body,
        "section": section,
        "lang": lang,
        "slug": slug,
        "old_path": old_path,
    }


def transform_page(page, classified, user_map, categories_raw):
    """Transform a single WP page into Hugo content."""
    title = clean_title(page["title"]["rendered"])

    slug = page["slug"]
    date = page["date"]

    front_matter = {
        "title": title,
        "date": date,
        "slug": slug,
    }

    # Determine language from URL patterns (pages lack WP categories)
    lang = detect_page_language(page)

    # Determine section from slug/URL pattern
    link = page.get("link", "")
    link_path = link.replace(WP_BASE, "").strip("/")
    link_lower = link_path.lower()

    # Map pages to sections based on URL structure
    section = "pages"
    if any(link_lower.startswith(p) for p in ["about", "statement", "what-is-platypus", "short-history",
                                               "about-platypus-deutsch", "uber-uns"]):
        section = "about"
    elif any(link_lower.startswith(p) for p in [
        "chapter", "chicago", "new-york", "london", "berlin",
        "toronto", "vienna", "boston", "thessaloniki", "athens",
        "hamburg", "jena", "cologne", "bielefeld", "frankfurt",
        "leipzig", "magdeburg", "bremen", "aarhus",
        "germany/", "greece/",
    ]):
        section = "chapters"
    elif "convention" in link_lower or "conference" in link_lower:
        section = "events"
    elif any(x in link_lower for x in ["reading-group", "pedagogy", "lesekreise"]):
        section = "reading-groups"
    elif "platypus-review" in link_lower or "review" in link_lower:
        section = "review"
    elif "texte-und" in link_lower:
        section = "review"

    html_content = page.get("content", {}).get("rendered", "")
    body = html_to_markdown(html_content)
    body = rewrite_urls(body)

    old_path = f"/{link_path}/" if link_path else None

    return {
        "front_matter": front_matter,
        "body": body,
        "section": section,
        "lang": lang,
        "slug": slug,
        "old_path": old_path,
    }


# ---------------------------------------------------------------------------
# File Writing
# ---------------------------------------------------------------------------

def write_hugo_content(item, content_dir):
    """Write a single Hugo content file."""
    section = item["section"]

    lang = item["lang"]
    if lang != "en":
        section_dir = content_dir / lang / section
    else:
        section_dir = content_dir / section

    section_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{item['slug']}.md"
    filepath = section_dir / filename

    # Build file content
    fm_str = yaml.dump(
        item["front_matter"],
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    ).strip()

    file_content = f"---\n{fm_str}\n---\n\n{item['body']}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(file_content)

    return filepath


def write_redirects(redirects, redirects_file):
    """Write Netlify _redirects file."""
    redirects_file.parent.mkdir(parents=True, exist_ok=True)

    lines = ["# Auto-generated redirects from WordPress migration\n"]
    for old_path, new_path in sorted(redirects):
        lines.append(f"{old_path} {new_path} 301")

    with open(redirects_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main Transform Pipeline
# ---------------------------------------------------------------------------

def transform_all():
    """Transform all fetched WP content into Hugo files."""
    # Load raw data
    print("Loading raw data...")
    with open(RAW_DIR / "posts.json", encoding="utf-8") as f:
        posts = json.load(f)
    with open(RAW_DIR / "pages.json", encoding="utf-8") as f:
        pages = json.load(f)
    with open(RAW_DIR / "categories.json", encoding="utf-8") as f:
        categories = json.load(f)
    with open(RAW_DIR / "tags.json", encoding="utf-8") as f:
        tags = json.load(f)
    users_path = RAW_DIR / "users.json"
    if users_path.exists():
        with open(users_path, encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []

    print(f"  Posts: {len(posts)}, Pages: {len(pages)}, "
          f"Categories: {len(categories)}, Tags: {len(tags)}, Users: {len(users)}")

    # Build lookup tables
    print("\nClassifying categories...")
    classified = classify_categories(categories)
    print(f"  Issue categories: {len(classified['issues'])}")
    print(f"  Author categories: {len(classified['authors'])}")
    print(f"  Speaker categories: {len(classified['speakers'])}")
    print(f"  Content type categories: {len(classified['content_types'])}")
    print(f"  Media type categories: {len(classified['media_types'])}")
    print(f"  Location categories: {len(classified['locations'])}")
    print(f"  Topic categories: {len(classified['topics'])}")
    print(f"  Skipped: {len(classified['skip'])}")

    user_map = {u["id"]: u["name"] for u in users}

    # Save classification for review
    classification_summary = {
        "issues": {str(k): v for k, v in sorted(classified["issues"].items(), key=lambda x: x[1])},
        "authors": {str(k): v for k, v in sorted(classified["authors"].items(), key=lambda x: x[1])},
        "content_types": {str(k): v for k, v in sorted(classified["content_types"].items(), key=lambda x: x[1])},
        "media_types": {str(k): v for k, v in sorted(classified["media_types"].items(), key=lambda x: x[1])},
        "locations": {str(k): v for k, v in sorted(classified["locations"].items(), key=lambda x: x[1])},
        "topics": {str(k): v for k, v in sorted(classified["topics"].items(), key=lambda x: x[1])},
        "topic_list": sorted(set(classified["topics"].values())),
    }
    with open(SCRIPT_DIR / "data" / "classification.json", "w", encoding="utf-8") as f:
        json.dump(classification_summary, f, ensure_ascii=False, indent=2)
    print(f"\n  Saved category classification to data/classification.json")

    # Transform posts
    print(f"\nTransforming {len(posts)} posts...")
    redirects = []
    stats = {}

    for i, post in enumerate(posts):
        item = transform_post(post, classified, user_map, categories)
        filepath = write_hugo_content(item, CONTENT_DIR)

        if item["old_path"]:
            lang = item["lang"]
            new_section = item["section"]
            if lang != "en":
                new_path = f"/{lang}/{new_section}/{item['slug']}/"
            else:
                new_path = f"/{new_section}/{item['slug']}/"
            redirects.append((item["old_path"], new_path))

        key = f"{item['lang']}/{item['section']}"
        stats[key] = stats.get(key, 0) + 1

        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1}/{len(posts)} posts...")

    print(f"  Posts by lang/section: {dict(sorted(stats.items()))}")

    # Transform pages
    print(f"\nTransforming {len(pages)} pages...")
    page_stats = {}

    for page in pages:
        item = transform_page(page, classified, user_map, categories)
        filepath = write_hugo_content(item, CONTENT_DIR)

        if item["old_path"]:
            lang = item["lang"]
            if lang != "en":
                new_path = f"/{lang}/{item['section']}/{item['slug']}/"
            else:
                new_path = f"/{item['section']}/{item['slug']}/"
            redirects.append((item["old_path"], new_path))

        key = f"{item['lang']}/{item['section']}"
        page_stats[key] = page_stats.get(key, 0) + 1

    print(f"  Pages by lang/section: {dict(sorted(page_stats.items()))}")

    # Write redirects
    print(f"\nWriting {len(redirects)} redirects...")
    write_redirects(redirects, REDIRECTS_FILE)

    # Summary
    print(f"\n{'='*60}")
    print("Migration complete!")
    print(f"{'='*60}")
    print(f"  Content files written to: {CONTENT_DIR}")
    print(f"  Redirects written to: {REDIRECTS_FILE}")
    print(f"  Total posts: {len(posts)}")
    print(f"  Total pages: {len(pages)}")
    print(f"  Total redirects: {len(redirects)}")

    # List content directory structure
    print(f"\nContent directory structure:")
    for dirpath, dirnames, filenames in os.walk(CONTENT_DIR):
        depth = len(Path(dirpath).relative_to(CONTENT_DIR).parts)
        indent = "  " * depth
        dirname = Path(dirpath).name
        count = len([f for f in filenames if f.endswith(".md")])
        if count > 0:
            print(f"  {indent}{dirname}/ ({count} files)")


# ---------------------------------------------------------------------------
# Incremental Sync
# ---------------------------------------------------------------------------

LAST_SYNC_FILE = SCRIPT_DIR / "data" / "last_sync.json"

# Files that should never be overwritten, even with --force
PROTECTED_PATTERNS = [
    "_index.md",
    "content/pages/publishing.md",
]

# Specific content files with manual frontmatter enhancements
PROTECTED_SLUGS = {
    "reading-groups": {"pedagogy", "primary-reading-group-archive",
                       "georgetown-spring-2023-reading-group-introduction-to-revolutionary-marxism"},
}


def is_protected(filepath):
    """Check if a file path is protected from overwrite."""
    filepath_str = str(filepath)
    if filepath.name == "_index.md":
        return True
    for pattern in PROTECTED_PATTERNS:
        if pattern in filepath_str:
            return True
    # Check section-specific protected slugs
    for section, slugs in PROTECTED_SLUGS.items():
        if f"/{section}/" in filepath_str:
            stem = filepath.stem  # filename without .md
            if stem in slugs:
                return True
    return False


def load_last_sync():
    """Load last sync timestamp, or None if never synced."""
    if LAST_SYNC_FILE.exists():
        with open(LAST_SYNC_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("last_sync")
    return None


def save_last_sync(timestamp, posts_synced, pages_synced):
    """Save sync state."""
    LAST_SYNC_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_SYNC_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "last_sync": timestamp,
            "posts_synced": posts_synced,
            "pages_synced": pages_synced,
        }, f, indent=2)


def fetch_since(since_date):
    """Fetch posts and pages modified after a given ISO date string.

    Also re-fetches categories (small payload, needed for classification).
    Returns (posts, pages, categories).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure ISO datetime format (WP requires T00:00:00 suffix)
    if "T" not in since_date:
        since_date = f"{since_date}T00:00:00"

    print(f"\nFetching content modified after {since_date}...")

    # Always re-fetch categories (small, needed for classification)
    print(f"\n{'='*60}")
    print("Fetching categories...")
    print(f"{'='*60}")
    categories = fetch_paginated("categories", {}, label="categories")
    cat_path = RAW_DIR / "categories.json"
    with open(cat_path, "w", encoding="utf-8") as f:
        json.dump(categories, f, ensure_ascii=False, indent=2)
    print(f"  -> Saved {len(categories)} categories")

    # Fetch posts modified after the date
    print(f"\n{'='*60}")
    print(f"Fetching posts modified after {since_date}...")
    print(f"{'='*60}")
    posts = fetch_paginated(
        "posts",
        {"status": "publish", "_embed": 1, "modified_after": since_date},
        label="posts",
    )
    print(f"  -> Found {len(posts)} modified posts")

    # Fetch pages modified after the date
    print(f"\n{'='*60}")
    print(f"Fetching pages modified after {since_date}...")
    print(f"{'='*60}")
    pages = fetch_paginated(
        "pages",
        {"status": "publish", "_embed": 1, "modified_after": since_date},
        label="pages",
    )
    print(f"  -> Found {len(pages)} modified pages")

    # Save sync data separately (don't overwrite full fetch files)
    sync_dir = RAW_DIR / "sync"
    sync_dir.mkdir(parents=True, exist_ok=True)
    with open(sync_dir / "posts.json", "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    with open(sync_dir / "pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

    return posts, pages, categories


def load_existing_redirects():
    """Load existing redirect paths from _redirects file."""
    existing = set()
    if REDIRECTS_FILE.exists():
        with open(REDIRECTS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 2:
                        existing.add(parts[0])
    return existing


def append_redirects(new_redirects):
    """Append new redirects to _redirects file (skip duplicates)."""
    existing = load_existing_redirects()
    to_add = [(old, new) for old, new in new_redirects if old not in existing]

    if not to_add:
        print("  No new redirects to add.")
        return 0

    with open(REDIRECTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n# Sync {datetime.now().isoformat()[:10]}\n")
        for old_path, new_path in sorted(to_add):
            f.write(f"{old_path} {new_path} 301\n")

    return len(to_add)


def sync_content(since=None, force=False):
    """Incrementally sync new content from WordPress.

    Fetches only posts/pages modified after `since` (or last sync date),
    transforms them, and writes only new files (skipping existing ones
    unless force=True). Appends new redirects.
    """
    # Determine cutoff date
    if since is None:
        since = load_last_sync()
    if since is None:
        print("Error: No previous sync found. Use --since YYYY-MM-DD or run a full 'fetch' + 'transform' first.")
        sys.exit(1)

    sync_timestamp = datetime.now().isoformat()

    # Fetch new content
    posts, pages, categories = fetch_since(since)

    if not posts and not pages:
        print("\nNo new content found. Everything is up to date.")
        save_last_sync(sync_timestamp, 0, 0)
        return

    # Classify categories
    print("\nClassifying categories...")
    classified = classify_categories(categories)

    # Load users (from existing raw data or empty)
    users_path = RAW_DIR / "users.json"
    if users_path.exists():
        with open(users_path, encoding="utf-8") as f:
            users = json.load(f)
    else:
        users = []
    user_map = {u["id"]: u["name"] for u in users}

    # Transform and write
    redirects = []
    written = 0
    skipped_existing = 0
    skipped_protected = 0

    # Posts
    print(f"\nTransforming {len(posts)} posts...")
    for post in posts:
        item = transform_post(post, classified, user_map, categories)
        lang = item["lang"]
        section = item["section"]
        if lang != "en":
            section_dir = CONTENT_DIR / lang / section
        else:
            section_dir = CONTENT_DIR / section
        filepath = section_dir / f"{item['slug']}.md"

        # Check protection
        if is_protected(filepath):
            print(f"  PROTECTED (skip): {filepath.relative_to(HUGO_ROOT)}")
            skipped_protected += 1
        elif filepath.exists() and not force:
            skipped_existing += 1
        else:
            section_dir.mkdir(parents=True, exist_ok=True)
            write_hugo_content(item, CONTENT_DIR)
            written += 1
            action = "UPDATED" if filepath.exists() else "NEW"
            print(f"  {action}: {filepath.relative_to(HUGO_ROOT)}")

        # Collect redirect
        if item["old_path"]:
            if lang != "en":
                new_path = f"/{lang}/{section}/{item['slug']}/"
            else:
                new_path = f"/{section}/{item['slug']}/"
            redirects.append((item["old_path"], new_path))

    # Pages
    print(f"\nTransforming {len(pages)} pages...")
    for page in pages:
        item = transform_page(page, classified, user_map, categories)
        lang = item["lang"]
        section = item["section"]
        if lang != "en":
            section_dir = CONTENT_DIR / lang / section
        else:
            section_dir = CONTENT_DIR / section
        filepath = section_dir / f"{item['slug']}.md"

        if is_protected(filepath):
            print(f"  PROTECTED (skip): {filepath.relative_to(HUGO_ROOT)}")
            skipped_protected += 1
        elif filepath.exists() and not force:
            skipped_existing += 1
        else:
            section_dir.mkdir(parents=True, exist_ok=True)
            write_hugo_content(item, CONTENT_DIR)
            written += 1
            action = "UPDATED" if filepath.exists() else "NEW"
            print(f"  {action}: {filepath.relative_to(HUGO_ROOT)}")

        if item["old_path"]:
            if lang != "en":
                new_path = f"/{lang}/{item['section']}/{item['slug']}/"
            else:
                new_path = f"/{item['section']}/{item['slug']}/"
            redirects.append((item["old_path"], new_path))

    # Append redirects
    print(f"\nProcessing redirects...")
    new_redirect_count = append_redirects(redirects)

    # Save sync state
    save_last_sync(sync_timestamp, len(posts), len(pages))

    # Summary
    print(f"\n{'='*60}")
    print("Sync complete!")
    print(f"{'='*60}")
    print(f"  Fetched: {len(posts)} posts, {len(pages)} pages")
    print(f"  Written: {written} files")
    print(f"  Skipped (already exists): {skipped_existing}")
    print(f"  Skipped (protected): {skipped_protected}")
    print(f"  New redirects: {new_redirect_count}")
    print(f"  Sync state saved to: {LAST_SYNC_FILE}")
    if skipped_existing > 0:
        print(f"\n  Tip: Use --force to overwrite existing (non-protected) files.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate platypus1917.org to Hugo")
    parser.add_argument(
        "command",
        choices=["fetch", "transform", "all", "sync"],
        help="fetch: full WP API download | transform: full content rewrite | "
             "all: fetch+transform | sync: incremental update",
    )
    parser.add_argument(
        "--since",
        help="ISO date for sync cutoff (default: last sync date). Example: 2026-03-01",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files during sync (protected files still skipped)",
    )
    args = parser.parse_args()

    if args.command in ("fetch", "all"):
        fetch_all()

    if args.command in ("transform", "all"):
        transform_all()

    if args.command == "sync":
        sync_content(since=args.since, force=args.force)


if __name__ == "__main__":
    main()
