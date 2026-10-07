# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all
three tool calls and returns a fit card — in at least 4 of 5 tries. The five
tries use five different queries, each matching at least one listing: `vintage graphic tee under $30`, `jeans under $40`, `denim jacket`,
`top size M`, `cargo pants`.

**Why this target:**
I picked 4 of 5 because my search is a plain keyword match and some phrasings will miss, like "tee shirt" when the data says "tee". Two of the three steps also call a model, which can get rate limited or come back empty, so I wanted room for one bad try without letting the main path be unreliable.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries. The five queries are fixed:
`designer ballgown size XXS under $5`, `tuxedo`, `wedding dress under $10`,
`tee under $1`, `saxophone`.

**Why this target:**
I picked 5 of 5 because this path never calls a model. It is just parsing the query, filtering, and an `if not results` check, so it gives the same answer every time. If it misses, that is a bug in my branch and not bad luck.

---

## 3. The item search found is the item the next tools received

In 5 of 5 happy-path runs (five different queries), the `id` in
`session["selected_item"]` equals `session["search_results"][0]["id"]`, equals
the `id` of the dict passed into `suggest_outfit`, and equals the `id` of the
dict passed into `create_fit_card`. I check it by wrapping both tools to record
the `id` they were called with, then comparing the three ids after the run.
Any mismatch in any of the five runs is a failure.

**Why this target:**
I picked 5 of 5 because nothing here is random. `run_agent` puts the item in the session and reads it back out, and no model decides which item gets passed. If the ids ever differ, something overwrote the session, and I want to see that every time. Comparing the whole dict instead of the id wouldn't add anything since each listing has a unique id.

---

## 4. The fit card is a postable caption that names the item's price and platform

Across 5 different items, each fit card is two to four sentences (a sentence
ends at `.`, `!` or `?` followed by a space, so a price like `$19.99` is not
a break), contains the
item's price (for example `$19`) and its platform name (for example `depop`,
case-insensitive), and no two of the five cards start with the same first six
words. At least 4 of the 5 cards must pass all three checks.

**Why this target:**
The model gives different words each run, so I can't check exact text, but I can check the things I'd be unhappy to miss: the price, the platform, a reasonable length, and openings that don't repeat. I picked 4 of 5 because the model will sometimes write a fifth sentence or skip the platform name. I didn't go lower because a caption without its own price isn't one I'd post.

---

## 5. Search respects the price ceiling and the size

For 5 queries that include a price ceiling and/or a size (for example
`jeans under $40`, `top size M`, `shoes size US 8`), 100% of the returned
listings are priced at or under the ceiling and match the size as a whole
token (an `S` request never returns `US 9` or `XL`; a `M` request may return
`S/M`). Zero violations across all five queries, checked by reading each
returned listing's `price` and `size` fields.

**Why this target:**
I picked zero violations because these filters are plain comparisons with no judgment in them. I chose this one because the size filter is the easiest thing to get quietly wrong. A plain substring test says `"s" in "us 9"` is True, so someone asking for a small top would just see shoes and think the search was broken.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
