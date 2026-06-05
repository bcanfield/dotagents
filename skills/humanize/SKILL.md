---
name: humanize
description: Write new prose or rewrite existing text so it doesn't read as AI-generated. Use whenever producing content a human will read as writing — blog posts, emails, READMEs, LinkedIn posts, docs, announcements, marketing copy — and always when the user says "humanize", "make this sound less like AI", "this sounds robotic", "rewrite this in my voice", or asks you to edit a draft for tone. Apply it even when the user doesn't mention AI: if the output is prose meant to sound like a person wrote it, this skill applies.
---

# Humanize

Make text read like a person wrote it. Works in two modes: **write** new content from scratch, or **rewrite** existing text. Both use the same pattern catalog below.

## Why surface edits aren't enough

AI writing has two layers of tells:

1. **Surface tells** — vocabulary, punctuation, sentence structure. Easy to fix mechanically. Fixing them beats casual readers and older statistical detectors.
2. **Content tells** — no specifics, no opinion, no discomfort, nothing only this author could have written. Modern classifiers (Pangram, Turnitin post-2025) survive synonym-swapping and paraphrasing at 90%+ because they key on these deeper patterns.

So: do the surface pass, but know that the content pass is what actually works. A paragraph with a real number, a named example, and a stated opinion reads human even with a "crucial" left in. A paragraph of polished generalities reads AI no matter how many words you swap.

## Surface tells

### Vocabulary and phrases

The exhaustive banned lists live in one place: `scripts/check_tells.py` (the audit runs it). Don't memorize them — internalize the principle: **prefer the plain word.** "Use," not "leverage." "Is," not "serves as." "Important," not "pivotal." If a word feels like it's dressing the sentence up, it probably came from the list. (If you can't execute the script, read it — the lists are at the top of the file.)

Highest-signal offenders to dodge while drafting: delve, leverage, crucial, pivotal, robust, seamless, landscape, tapestry, testament, foster, showcase, underscore, boasts, meticulous, vibrant, game-changer. Newer models lean less on these and more on the -ing forms — **emphasizing, highlighting, showcasing, enhance, align with** — watch those especially.

Same goes for stock phrases. The iconic ones: "In today's fast-paced world," "It's important to note," "I'm excited to share," "Let's dive in," "Here's the thing," "In conclusion," the "Whether you're a beginner or an expert" closing recap, and chat residue like "I hope this helps!" or "Great question!" Full list in the script.

**Transitions:** two formal connectors (moreover, furthermore, additionally, thus, hence...) per piece is plenty; mostly a sentence needs no transition word at all.

### Structures — the strongest tells

These matter more than vocabulary. Readers and platforms (LinkedIn now demotes some of these algorithmically) pattern-match on structure.

**Negative parallelism.** "It's not just X, it's Y." "Not only A, but B." "This isn't about X — it's about Y." The single most recognized AI tell right now. Just state Y. The split-sentence variant ("What I got wrong wasn't X. It was Y.") is the same move across a sentence boundary — one per piece at most, and only when the contrast is the actual point.

**Rule of three.** Triplets everywhere: three adjectives, three benefits, three-item lists. Humans use ones, twos, and fours too. Break the triples.

**Em dash overuse.** LLMs drop em dashes where humans use commas, parentheses, or a period. One or two per piece is human; one per paragraph isn't.

**Rhetorical reveals.** "The result? Disaster." "The brutal truth?" "What does this mean? It means..." Infomercial pacing. Make the point directly.

**Question-format headings.** "What Is X?" / "Why Does Y Matter?" Use declarative headings, sentence case.

**Copula avoidance.** "serves as," "stands as," "represents," "marks" instead of plain "is." Write "is."

**-ing significance tails.** A clause bolted on to inflate meaning: "..., symbolizing the broader shift toward distributed teams." Cut the tail; if the significance is real, give it its own concrete sentence.

**False ranges.** "From bustling cities to serene landscapes," "from beginners to experts." Name actual items or cut.

**Vague attribution.** "Experts argue," "studies show," "many believe," "such as" before a padded list. Name the expert or the study, or own the claim yourself.

**Hedging stacks.** "could potentially possibly" → "may." One hedge max.

**Mirror structure.** Consecutive sentences with identical shapes ("X does A. Y does B. Z does C."). Break the symmetry.

**Neat paragraph endings.** Every paragraph closing with a tidy mini-conclusion is a model habit. Let roughly a third of paragraphs just stop when the point is made.

**Symmetric formatting.** Bold-headed bullets of identical length, emoji bullets, Title Case Headings, a bolded key phrase in every paragraph. Vary or strip.

**Synonym cycling.** Calling the same thing "the platform," then "the solution," then "the tool" to dodge repetition. Repeating a word is fine. Say it once, well.

**Formulaic wrap-ups.** "Despite these challenges, X continues to thrive." Section-end summaries that repeat the section. End when you're done saying the thing.

**Register mismatch.** Government-memo formality in a casual context (no contractions, "individuals" for "people," "utilize" for "use"). Match the register the situation calls for.

**The treadmill test.** If paragraphs could be reshuffled without losing anything, there's no argument — just topic-adjacent statements. Each paragraph should need the one before it.

**Leaked artifacts** (rewrite mode especially): `[Your Name]`-style placeholders, `oai_citation`/`citeturn0search0` markup, `utm_source=chatgpt.com` in links, curly quotes in a straight-quote codebase. Strip all of it.

### Rhythm

Statistical detectors measured exactly this: humans vary, models don't.

- Vary sentence length hard. Follow a 30-word sentence with a 4-word one. It works.
- Vary paragraph length too — including the occasional one-line paragraph.
- Use contractions. "You'll," "doesn't," "it's."
- Starting a sentence with And, But, or So is fine. Humans do it constantly.
- Cut filler: "in order to" → "to," "due to the fact that" → "because," "in terms of" → usually nothing.

## Content tells — the pass that matters

Surface-clean text still reads AI if it could have been written about any topic by anyone. For each paragraph, ask: **could someone who knows nothing about this subject have written this?** If yes, rewrite or cut.

- **Be specific.** Numbers, names, dates, file paths, error messages, prices, version numbers. "Deploys went from 40 minutes to 6" beats "significantly improved deployment efficiency."
- **Have a position.** AI writing balances both sides into mush. Pick a side, say it, and let one counterpoint in if it's real.
- **Allow discomfort.** AI text never expresses frustration, doubt, or boredom — every setback is a "learning opportunity." Real writing says "this part sucked" or "I'm still not sure this was right."
- **Cut the throat-clearing.** Get to the point in sentence one. No paragraph explaining what the piece will cover.
- **Don't over-explain.** Trust the reader. If a sentence restates the previous one in different words, delete it. Density beats length.

## Process

### Mode: write new content

1. Get the specifics before drafting. If you don't have concrete details (real numbers, real names, what actually happened), ask for them or pull them from available context — never pad with generalities.
2. Draft with the catalog in mind, but write for the reader first; don't produce stilted text just to dodge tells.
3. Run the audit (below).

### Mode: rewrite existing text

1. Read the whole text first. Identify what it's actually trying to say and what real substance it contains.
2. Rewrite — don't patch. Word-swapping a bad structure leaves the structure. Rebuild sentences around the substance.
3. Preserve meaning, claims, and any facts exactly. Never invent statistics, sources, or anecdotes. If a claim leans on a missing specific, prefer rephrasing it so it stands without one; use a bracketed flag like "[add the actual metric]" only when the claim is unusable without it — the deliverable should be paste-ready, not a template.
4. Run the audit (below).

### The audit — always do this

After your draft, make a second pass as a skeptical reader who suspects the text is AI-generated:

1. If you can execute scripts, run the bundled checker on the draft — `python3 <this skill's base directory>/scripts/check_tells.py <file>` — for a deterministic scan of banned words, phrases, negative parallelism, em dashes, rhythm, and artifacts. Fix every FAIL.
2. Then scan for what the script can't catch: rule of three, mirror structure, rhetorical reveals, neat endings, synonym cycling, vague attribution, the treadmill test. First drafts almost always retain a few.
3. Beware **secondary convergence**: don't swap one cliché for another. The fix for "delve" is not "embark"; the fix for "It's not X, it's Y" is not "The truth? Y." If your replacement is on the catalog too, restructure the sentence instead.
4. Check content: point to the sentence only this author could have written. If you can't find one per few paragraphs, the text is still slop.
5. Fix what you found. One audit-and-fix pass minimum; repeat if the first audit found more than a couple of issues.

### Voice matching (when samples exist)

If you have 2–3 samples of the author's real writing (or the user can provide them), match those instead of writing toward a generic "human" voice: their sentence rhythm, typical word choices, how formal they get, quirks like one-word sentences or parentheticals. A matched voice beats a neutral humanized one every time.

## What not to do

- Don't inject fake typos, slang, or forced idioms to "seem human." Stilted-casual is its own tell.
- Don't invent metrics, dollar amounts, named sources, or verifiable events. Rephrase so the claim stands without them, or flag for the author. Plausible narrative texture is different: when ghost-writing first-person content, ordinary connective detail (rough timelines, "we argued about it") is fine and usually necessary — hard numbers and citations are not.
- Don't sacrifice clarity for pattern-avoidance. A clear sentence with one "key" in it beats a contorted one without.
