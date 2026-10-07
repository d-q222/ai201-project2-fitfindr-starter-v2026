"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings
import re


# ── Tool 1: search_listings ───────────────────────────────────────────────────

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with"
}

def _stem(word: str) -> str:
    """Crude plural fold so "tees" matches "tee" and "jeans" matches "jean"."""
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """Lowercase, stemmed words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {_stem(w) for w in words if w not in _STOPWORDS and len(w) > 1}


def _size_tokens(size: str) -> set[str]:
    """
    Break a size string into whole-token pieces.

    "S/M" -> {"S", "M"}, "XL (oversized)" -> {"XL"}, "W30 L30" -> {"W30", "L30"}.
    Whole tokens are the point: "M" must match "S/M" but "S" must not match
    "US 9", and "L" must not match "XL".
    """
    cleaned = re.sub(r"\([^)]*\)", " ", size or "").upper()
    cleaned = re.sub(r"\bUS\s*(\d)", r"US\1", cleaned)  # "US 8" is one token
    return {t for t in re.split(r"[/\s,]+", cleaned) if t}


def _size_matches(wanted: str | None, listing_size: str) -> bool:
    if not wanted:
        return True
    if (listing_size or "").strip().upper().startswith("ONE SIZE"):
        return True  # one-size items fit any request
    wanted_tokens = _size_tokens(wanted)
    return bool(wanted_tokens & _size_tokens(listing_size))


def _score(listing: dict, wanted: set[str]) -> int:
    """Keyword overlap, with title words counting double."""
    title = _keywords(listing.get("title"))
    other = _keywords(
        " ".join(
            [
                listing.get("description") or "",
                listing.get("category") or "",
                listing.get("brand") or "",
                " ".join(listing.get("style_tags") or []),
                " ".join(listing.get("colors") or []),
            ]
        )
    )
    return 2 * len(wanted & title) + len(wanted & (other - title))


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.


    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    wanted = _keywords(description)
    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if not _size_matches(size, listing["size"]):
            continue
        score = _score(listing, wanted)
        if score > 0:
            scored.append((score, listing))

    # Highest score first; cheaper first on ties.
    scored.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.


    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
    item_line = (
        f"{new_item.get('title')} ({new_item.get('category')}, "
        f"{', '.join(new_item.get('colors') or [])}; "
        f"style: {', '.join(new_item.get('style_tags') or [])})"
    )
    system = (
        "You are a thrift-store stylist. Be specific and brief: one or two "
        "outfits, no preamble."
    )

    if not items:
        prompt = (
            f"Someone is considering this thrifted piece: {item_line}.\n"
            "They haven't told me what they own, so give general styling "
            "advice: one or two outfit ideas built from common basics, and "
            "say what kind of pieces would pair well with it."
        )
    else:
        owned = "\n".join(
            f"- {w.get('name')} ({w.get('category')}; "
            f"{', '.join(w.get('colors') or [])})"
            + (f" — {w['notes']}" if w.get("notes") else "")
            for w in items
        )
        prompt = (
            f"Someone is considering this thrifted piece: {item_line}.\n"
            f"Their wardrobe:\n{owned}\n\n"
            "Suggest one or two outfits that combine the new piece with items "
            "from their wardrobe. Name the wardrobe pieces exactly as listed."
        )

    text = generate(prompt, system=system, cache=config.CACHE_ENABLED)
    return text.strip() or "Pair it with simple basics in a neutral colour."


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time


    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not (outfit or "").strip():
        return (
            "No fit card written: there was no outfit suggestion to base it "
            "on. Run suggest_outfit first."
        )

    system = (
        "You write short social-media captions for thrift finds. Casual, "
        "specific, first person. No hashtag walls."
    )
    prompt = (
        f"Item: {new_item.get('title')}\n"
        f"Price: ${new_item.get('price'):g}\n"
        f"Platform: {new_item.get('platform')}\n"
        f"Outfit idea: {outfit}\n\n"
        "Write a two-to-four sentence caption someone would post. Mention the "
        "item, the price and the platform once each, and be specific about "
        "the vibe. Return only the caption."
    )
    text = generate(prompt, system=system, cache=config.CACHE_ENABLED)
    return text.strip()
