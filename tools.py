"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


_STOPWORDS = {
    "a",
    "an",
    "and",
    "any",
    "for",
    "in",
    "is",
    "like",
    "looking",
    "me",
    "my",
    "of",
    "on",
    "please",
    "size",
    "that",
    "the",
    "this",
    "to",
    "under",
    "want",
    "with",
}


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    listings = load_listings()

    def normalize(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

    def tokenize(text: str) -> list[str]:
        normalized = normalize(text)
        tokens = [token for token in normalized.split() if token and token not in _STOPWORDS]
        return tokens or ([normalized] if normalized else [])

    query_tokens = tokenize(description)
    query_phrase = normalize(description)
    matches: list[tuple[float, dict]] = []

    for listing in listings:
        if max_price is not None and float(listing.get("price", 0)) > float(max_price):
            continue

        listing_size = str(listing.get("size", ""))
        if size is not None and size.strip():
            if size.lower() not in listing_size.lower():
                continue

        title = normalize(str(listing.get("title", "")))
        description_text = normalize(str(listing.get("description", "")))
        category = normalize(str(listing.get("category", "")))
        style_tags = " ".join(str(tag) for tag in listing.get("style_tags", []))
        style_tags_text = normalize(style_tags)
        colors_text = normalize(" ".join(str(color) for color in listing.get("colors", [])))
        brand_text = normalize(str(listing.get("brand", "")))
        searchable_text = " ".join(
            part for part in [title, description_text, category, style_tags_text, colors_text, brand_text] if part
        )

        score = 0.0
        if query_phrase and query_phrase in searchable_text:
            score += 5.0

        for token in query_tokens:
            if token in title:
                score += 3.0
            if token in style_tags_text:
                score += 3.0
            if token in description_text:
                score += 2.0
            if token in category:
                score += 1.5
            if token in colors_text or token in brand_text:
                score += 1.0

        if score > 0:
            matches.append((score, listing))

    matches.sort(key=lambda item: (-item[0], float(item[1].get("price", 0)), str(item[1].get("title", ""))))
    return [listing for _, listing in matches]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    items = wardrobe.get("items", []) if isinstance(wardrobe, dict) else []
    wardrobe_lines = []
    for item in items:
        wardrobe_lines.append(
            f"- {item.get('name', 'Unnamed item')} | category: {item.get('category', 'unknown')} | colors: {', '.join(item.get('colors', [])) or 'none'} | style tags: {', '.join(item.get('style_tags', [])) or 'none'} | notes: {item.get('notes') or 'none'}"
        )

    item_summary = (
        f"Title: {new_item.get('title', 'Unknown item')}\n"
        f"Description: {new_item.get('description', 'No description provided')}\n"
        f"Category: {new_item.get('category', 'unknown')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', [])) or 'none'}\n"
        f"Size: {new_item.get('size', 'unknown')}\n"
        f"Condition: {new_item.get('condition', 'unknown')}\n"
        f"Price: ${float(new_item.get('price', 0)):.2f}\n"
        f"Platform: {new_item.get('platform', 'unknown')}"
    )

    if wardrobe_lines:
        prompt = (
            "You are FitFindr, a thrift styling assistant. Suggest 1-2 specific outfits for the new item using pieces from the wardrobe. "
            "Mention exact wardrobe item names, explain why they work together, and include one or two styling tips. Keep it concise but useful.\n\n"
            f"New item:\n{item_summary}\n\n"
            "Wardrobe items:\n"
            + "\n".join(wardrobe_lines)
        )
    else:
        prompt = (
            "You are FitFindr, a thrift styling assistant. The user has no saved wardrobe items, so give general styling advice based on the new item alone. "
            "Suggest what types of pieces would pair well, the overall vibe, and a couple styling tips. Keep it concise but useful.\n\n"
            f"New item:\n{item_summary}"
        )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You write practical, fashion-forward outfit suggestions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        if content:
            return content
    except Exception:
        pass

    style_tags = ", ".join(new_item.get("style_tags", [])[:3]) or "the item's style"
    title = new_item.get("title", "this piece")
    if items:
        first_item = items[0]
        wardrobe_name = first_item.get("name", "your wardrobe")
        return (
            f"Pair {title} with {wardrobe_name} for a look that leans {style_tags}. "
            f"Add a clean layer and keep the accessories simple so the item stays the focus."
        )
    return (
        f"{title} has strong {style_tags} energy. Try pairing it with high-waisted denim, chunky shoes, and one clean layer to keep the outfit balanced."
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    if not outfit or not outfit.strip():
        return "Unable to generate fit card, outfit suggestion was incomplete. Try searching for a different item."

    item_summary = (
        f"Title: {new_item.get('title', 'Unknown item')}\n"
        f"Price: ${float(new_item.get('price', 0)):.2f}\n"
        f"Platform: {new_item.get('platform', 'unknown')}\n"
        f"Condition: {new_item.get('condition', 'unknown')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', [])) or 'none'}"
    )

    prompt = (
        "You are FitFindr writing a short, shareable outfit caption. "
        "Write 2-4 sentences that sound casual and authentic, like a real OOTD caption. "
        "Mention the item name, price, and platform naturally exactly once each. "
        "Do not sound like a product listing. Include 1-3 relevant emojis. "
        "Make it vivid and specific to the outfit vibe.\n\n"
        f"New item details:\n{item_summary}\n\n"
        f"Outfit suggestion:\n{outfit}"
    )

    try:
        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You write punchy, authentic thrift fit captions."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
        )
        content = response.choices[0].message.content.strip()
        if content:
            return content
    except Exception:
        pass

    title = new_item.get("title", "this find")
    platform = new_item.get("platform", "depop")
    price = float(new_item.get("price", 0))
    outfit_snippet = outfit.strip().split(".")[0]
    return f"grabbed {title.lower()} off {platform} for ${price:.0f} and it totally matches the vibe 🖤 {outfit_snippet}"
