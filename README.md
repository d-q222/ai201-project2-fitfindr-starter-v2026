# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are built now, so that last command runs the whole agent.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

This is a tool that helps you search through thrift listings. You type in what you want, like a vintage graphic tee under $30, and it searches the listings and picks the best match. Then it looks at your wardrobe and suggests outfits that use pieces you already own, and writes a short caption you could post about the find. If nothing matches, it stops and tells you what to change, like the words, the size, or the price. If your wardrobe is empty, it gives general styling advice instead.

---

## Tool Inventory

### `search_listings`

- **What it does:** Searches the listings file for items matching a description, optionally filtered by size and a price ceiling. It does not call a model.
- **Inputs:** `description` (str) — keywords like "vintage graphic tee"; `size` (str or None) — e.g. "M"; `max_price` (float or None) — inclusive ceiling.
- **Returns:** A list of listing dicts, best match first, at most 10 (`config.SEARCH_RESULT_LIMIT`). Each dict has `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None) and `platform`. Score is keyword overlap with title words counting double; cheaper listing wins ties. A size matches as a whole token, so "M" matches "S/M" and "M/L" but "S" never matches "US 9" and "L" never matches "XL". "One Size" listings match any size.
- **When it has nothing:** An empty list `[]`. Not `None`, not an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits that combine the new item with pieces from the user's wardrobe.
- **Inputs:** `new_item` (dict) — a listing dict; `wardrobe` (dict) — has an `items` key holding a list of wardrobe item dicts (`name`, `category`, `colors`, `style_tags`, `notes`).
- **Returns:** A non-empty string of outfit suggestions that name wardrobe pieces exactly as they are listed.
- **When it has nothing:** If `wardrobe["items"]` is empty it still returns a string, general styling advice for the item built from common basics. It never returns `""` and never raises.

### `create_fit_card`

- **What it does:** Asks the model to write a short caption someone would actually post about the find.
- **Inputs:** `outfit` (str) — the string from `suggest_outfit`; `new_item` (dict) — the listing dict.
- **Returns:** A two-to-four sentence caption (str) that mentions the item, its price and its platform. It is different on different runs (temperature is 0.9).
- **When it has nothing:** If `outfit` is empty or only whitespace it returns the message "No fit card written: there was no outfit suggestion to base it on. Run suggest_outfit first." instead of raising.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names the description, size and price that were tried and what to change, and return the session without calling `suggest_outfit` or `create_fit_card` (so `session["fit_card"]` stays `None`). Otherwise take the first result, put it in `session["selected_item"]`, and go on to `suggest_outfit`, then `create_fit_card`.

**Second branch (stretch):** If the search is empty *and* a size was given, the loop retries the same search with the size dropped. If that finds something it sets `session["note"]` saying the size filter was dropped and continues; if it is still empty, the first branch rule applies.

**Where it lives:** `agent.py::run_agent` (the message is built by `agent.py::_nothing_found_message`)

**How the query is parsed:** Regex, in `agent.py::parse_query`. It pulls out a price (`under $30`, `$30`), a size (`size M`, or a bare `, M` at the end) and leaves the rest as the description. I chose regex over asking the model because it costs nothing and gives the same answer twice. What it gives up is phrasing it hasn't seen: "nothing over thirty dollars" parses to no price, so the ceiling is silently ignored.

**What moves through the session:** `query` → `parsed` (description, size, max_price) → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. Each step reads its input back out of the session rather than getting it passed straight from the last call. `error` is set when the run ends early and `note` when the size was relaxed.

---

## Sample Run

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Vintage Band Tee — Faded Grey — $19.0 on depop

  Outfit:   **Outfit 1 (Grunge Streetwear):**
Pair the vintage band tee with the baggy straight-leg jeans, black denim jacket, and black combat boots. Accessorize with the brown leather belt and black crossbody bag.

**Outfit 2 (Layered Casual):**
Layer the white ribbed tank top under the vintage band tee, worn tucked into the wide-leg khaki trousers. Pair with chunky white sneakers and the black crossbody bag.

  Fit card: That perfect, perfectly worn-in grey fade you can only get from decades of actual concerts. Throwing this vintage band tee up on Depop for $19. It looks insanely good layered over a ribbed tank with wide-leg khakis, or just beat up with your favorite combat boots.
```

And a query that matches nothing, which stops at the branch:

```
$ python app.py ask 'designer ballgown size XXS under $5'

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(r['title'],r['price'],r['size']) for r in search_listings('graphic tee', max_price=30)])"
[('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('Vintage Band Tee — Faded Grey', 19.0, 'L'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L'), ('Oversized Crewneck Sweatshirt — Vintage Navy', 20.0, 'XL (fits oversized)'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29')]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
**Outfit 1**
- Vintage Levi's 501 Jeans — Medium Wash
- White ribbed tank top
- Vintage black denim jacket
- Chunky white sneakers
- Black crossbody bag

**Outfit 2**
- Vintage Levi's 501 Jeans — Medium Wash
- Oversized grey crewneck sweatshirt
- Black combat boots
- Brown leather belt
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Nothing beats broken-in vintage Levi's 501s in that perfect medium wash. Just add your favorite crisp white sneakers and a simple tee for the ultimate effortless 90s off-duty look. Grab them on my depop now for $38 before they're gone.
```

---

## How I Used AI

I used a web AI tool for this project. I worked on my own, so I used it for the peer advice parts and for debugging.

**Moment 1**

- What I asked for: I pasted my five acceptance criteria in and asked how it would test each one using only what the sentence says, with no suggestions for improving them.
- What came back:
  a. Matching query completes all three tools: Testable. Run 5 queries that match a listing and count how many return a fit card. Pass at 4 or more. It can't say which 5 queries to use, so it would have to invent them.
  b. Impossible query stops before the second tool: Testable. Run 5 nonsense queries and check that suggest_outfit is never called and the returned message names something to change. "Naming what to change" is slightly fuzzy, because it doesn't say how many things or which ones.
  c. Same item all the way through: Testable. It gives the exact method: wrap both tools to record ids, then compare the three ids. It still needs five different queries from somewhere.
  d. Fit card is a postable caption: Mostly testable. Count sentences (2–4), look for the price and platform, and compare the first six words across cards. "Sentence" isn't defined, so a price like $19.99 could be miscounted as a sentence break. "Postable" is covered only by those three checks.
  e. Search respects price and size: Testable. Read price and size on each returned listing. The one ambiguity is One Size / Oversized. The sentence doesn't say whether it counts as a match for S, and the code returns it.
-  What I changed: I reworded criteria 1 and 4 and left the other three as they were. For 1, I added that the five queries have to be different ones that each match at least one listing, because it couldn't tell which queries to run. For 4, I said a sentence ends at ., ! or ? followed by a space, so a price like $19.99 doesn't get counted as two sentences.

**Moment 2 (debugging Milestone 4)**

- What I asked for: I pasted in the message my agent shows when a search comes back empty and asked what I would try next if I knew nothing about the app.
- What came back: I ran _nothing_found_message on two queries. For wizard robe size XXS under $5:
▎ Nothing in the listings matched description 'wizard robe', size XXS, under $5. Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.

  Someone who knew nothing about the app would try dropping the size first, then raising the price, then shortening the description. The message works because it lists only the filters that were actually set. For purple tuxedo it suggests only broader words. One gap is that it never says what kinds of items exist, so "broader words" is a guess. "A neighbouring one" for size also assumes the user knows which sizes are neighbours.
- What I changed: I didn't change _nothing_found_message in agent.py. It already said what I'd try next, because it only lists the things I actually set (description, size, price) and gives one fix for each. A search with no size never tells you to drop the size, which is what I wanted.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
