# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Overview:** FitFindr's job is to take a natural language search query, find matching secondhand listings, evaluate how they fit with what the user already owns, and create a shareable outfit description. If search_listings returns empty results or suggest_outfit fails, the agent communicates that to the user and stops it doesn't proceed with garbage input.

**Step 1:** Parse and search
- Agent extracts from the query: description="vintage graphic tee", size=None (not mentioned), max_price=30.0
- Calls search_listings("vintage graphic tee", None, 30.0)
- Returns matching listings like [{"id": "lst_033", "title": "Vintage Band Tee — Faded Grey", "description": "Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.", "category": "tops", "style_tags": ["vintage", "grunge", "band tee", "graphic tee", "streetwear"], "size": "L", "condition": "fair", "price": 19.00, "colors": ["grey", "charcoal"], "brand": null, "platform": "depop"}, ...]
- Agent stores top result in session["selected_item"] and proceeds to next tool

**Step 2:** Suggest outfit
- Agent calls suggest_outfit(new_item=<band tee from step 1>, wardrobe=<user's wardrobe>)
- LLM sees user has: baggy dark wash jeans, chunky white sneakers, black combat boots, vintage black denim jacket, grey sweatshirt
- LLM considers the item: faded grey band tee (boxy fit, vintage grunge style)
- Returns: "Pair this faded band tee with your baggy dark wash jeans and chunky white sneakers for that authentic 90s grunge aesthetic. Layer your vintage black denim jacket over it. Roll the sleeves once to show the distressing and add some dimension. Tuck just the front corner slightly into your jeans for a subtle fitted look that balances the boxy tee."
- Agent stores this in session["outfit_suggestion"]

**Step 3:** Create fit card
- Agent calls create_fit_card(outfit=<suggestion from step 2>, new_item=<band tee>)
- LLM generates a shareable Instagram-style caption using the actual listing details (title, price, platform, condition)
- Returns: "grabbed this faded band tee off depop for $19 and the distressed graphic hits different 🖤 pairs perfectly with my baggy jeans and chunky sneakers. vintage grunge is SO the move"
- Agent stores in session["fit_card"]

**Final output to user:**
The user sees three panels:
1. **Listing details:** "Vintage Band Tee — Faded Grey | Depop | $19.00 | Fair condition | Style: vintage, grunge, band tee, graphic tee, streetwear | Size: L | Colors: grey, charcoal"
2. **Outfit suggestion:** "Pair this faded band tee with your baggy dark wash jeans and chunky white sneakers for that authentic 90s grunge aesthetic. Layer your vintage black denim jacket over it..."
3. **Fit card:** "grabbed this faded band tee off depop for $19 and the distressed graphic hits different 🖤 pairs perfectly with my baggy jeans and chunky sneakers. vintage grunge is SO the move"
