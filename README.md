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

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
$ python -c "from tools import suggest_outfit; ..."

```

```
$ python -c "from tools import create_fit_card; ..."

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

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
