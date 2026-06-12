# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:

```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:

```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

## Tool Inventory

### search_listings(description, size, max_price)

Purpose: Search the mock listings dataset for secondhand items that match the user's request.

Inputs: `description` (str) for keyword matching, `size` (str or None) for optional size filtering, and `max_price` (float or None) for optional price filtering.

Output: A list of listing dicts sorted by relevance, or `[]` if nothing matches.

### suggest_outfit(new_item, wardrobe)

Purpose: Use Groq's LLM to suggest 1–2 outfits for the selected listing using the user's wardrobe.

Inputs: `new_item` (dict) for the selected listing, and `wardrobe` (dict) for the user's closet items.

Output: A styling paragraph or short multi-part outfit suggestion string.

### create_fit_card(outfit, new_item)

Purpose: Turn the outfit suggestion into a short, shareable caption.

Inputs: `outfit` (str) for the styling suggestion, and `new_item` (dict) for the selected listing details.

Output: An Instagram-style caption string, or an error message string if the outfit input is missing.

## Planning Loop

FitFindr follows a simple decision tree. First, it parses the user's query into description, size, and max price. Then it calls `search_listings`. If that returns no results, it stops early and returns an error message to the user. If there is at least one match, it stores the top result in session state, calls `suggest_outfit` with that item and the wardrobe, then calls `create_fit_card` with the outfit text and the same item. The loop ends by returning the full session object.

## State Management

I keep all intermediate data in one session dictionary so each tool can build on the previous one without re-asking the user for the same information.

What I store:

- Original query text
- Parsed description, size, and max price
- Full search results
- The selected top listing
- The wardrobe input
- The outfit suggestion text
- The fit card caption
- Any error message

How it flows:

- `search_listings` writes into `search_results`
- The first result becomes `selected_item`
- `suggest_outfit` writes into `outfit_suggestion`
- `create_fit_card` writes into `fit_card`

## Error Handling

- `search_listings`: If nothing matches, the agent returns a clear message telling the user to try different keywords, a higher budget, or a different size filter.
- `suggest_outfit`: If the wardrobe is empty, the agent still gives general styling advice instead of failing.
- `create_fit_card`: If the outfit input is empty, the agent returns a short error message instead of crashing.

## Spec Reflection

One thing the spec helped with was keeping the control flow honest: the no-results branch is clearly defined, so the agent does not continue with bad input. One place the implementation drifted a little was query parsing, because real user phrasing was messier than the original sketch. I tightened the parser after testing so it would not mistake a price like `$30` for a size.

## AI Usage

1. I gave Claude the `search_listings` spec from planning.md and asked it to implement filtering and scoring against the real dataset. I kept the fallback logic and test cases I had planned, then adjusted the parser after seeing how the first result was ranked.

2. I gave Claude the planning-loop and state-management sections plus the Mermaid diagram from planning.md and asked it to wire `run_agent()` and `handle_query()`. I kept the branch structure, but I revised the query parsing after testing showed that it could misread price text as a size.

## Demo Video

A 3-5 minute walkthrough of FitFindr's full agent flow. I start by briefly
introducing the project, then run a happy-path query (for example, a vintage
graphic tee under $30) to show all three tools in sequence: listing search,
outfit suggestion, and fit card generation. During the walkthrough, I point out
that the selected item is stored in session state and reused across tools.
I then run an impossible query (designer ballgown size XXS under $5) to show
the failure branch where search returns no matches and the agent exits early
with a clear error message instead of calling later tools.

**[Watch the demo (demo.mp4)](demo.mp4)**
