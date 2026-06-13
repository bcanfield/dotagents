---
name: agents-md
description: Create, update, audit, and maintain AGENTS.md, CLAUDE.md, .cursorrules, GEMINI.md, copilot-instructions, or similar coding-agent instruction files, using evidence-based best practices. This covers setting up or bootstrapping such a file for a repo or service ("set up a CLAUDE.md", "bootstrap agent docs", "init"); cleaning up, trimming, shortening, or fixing a bloated file the agent seems to ignore; advice on what content belongs in these files; deciding between one root file vs. per-package files in a monorepo; and consolidating drifting per-tool files (Cursor, Claude Code, Codex, Copilot) into one canonical file with symlinks or imports. Also use when the user never names a file but wants coding agents to know repo-specific commands, conventions, or gotchas — they say "document this for the agent", "make sure Claude knows about X", "add this to the project instructions", the agent keeps guessing commands wrong or repeating a mistake, or a change added commands, env vars, or conventions agents must know. Handles both doing the work and answering best-practice questions about these files.
---

# AGENTS.md — create, update, and maintain agent instruction files

An AGENTS.md (or CLAUDE.md — same concept, different filename) is loaded into **every** agent session in the repo. That makes it the highest-leverage file in the project, and also the easiest to ruin: every line spends from a fixed attention budget shared by all the other lines.

The evidence (full citations in `references/evidence.md`):

- Frontier models reliably follow only **~150–200 simultaneous instructions**, and the agent's own system prompt already consumes ~50 of those. Adherence degrades **across the whole file** as instruction count grows — adding a rule weakens every existing rule. The dominant failure mode is silent omission, not misinterpretation.
- A 2026 ETH Zurich/LogicStar benchmark found **developer-written** context files improved task success ~4%, while **LLM-generated** (bloated, overview-heavy) files made agents *worse* in 5 of 8 settings while raising cost ~20%. Codebase overviews measurably did nothing. Agents follow these files *too* well — anchoring on stale or irrelevant content.
- Top-performing files across a 2,500-repo corpus averaged **300–350 words**. Anthropic's guidance: under 200 lines, and "bloated CLAUDE.md files cause Claude to ignore your actual instructions."

So the prime directive of this skill: **the file is a budget, not a wiki.** Every operation below — creating, updating, auditing — is an exercise in deciding what *earns* a line, not what could fill one.

## The per-line litmus test

A line earns its place only if all three hold:

1. **Not discoverable** — the agent couldn't learn it by reading the code, manifests, or lint config.
2. **Operationally significant** — getting it wrong causes real damage or wasted work.
3. **Not guessable by convention** — a competent agent wouldn't infer it from standard practice.

Anthropic's one-question version: *"Would removing this line cause the agent to make mistakes?"* If not, cut it.

What passes: build/test commands with non-obvious flags, deviations from language defaults, env vars that must be set, "legacy/ looks dead but production imports it", repo etiquette (commit format, branch rules), hard boundaries (never touch X without review).

What fails: directory maps, tech-stack overviews, file-by-file descriptions, anything a linter already enforces, standard conventions ("write tests", "use meaningful names"), detailed API docs (link instead), frequently-changing facts (they go stale and stale instructions actively misdirect).

## The routing rule — not everything belongs in this file

Before adding content, route it to the right mechanism:

| Content | Destination |
|---|---|
| Broadly-applicable fact every session needs | AGENTS.md |
| Multi-step procedure used occasionally | A skill, or a doc linked by pointer with a one-line description |
| Rule that must hold 100% of the time | A hook or lint rule — instruction-file text is advisory, never enforced |
| Knowledge relevant to one part of the codebase | Nested AGENTS.md in that directory, or path-scoped rules |
| Something the codebase could enforce structurally | Fix the codebase (add the lint rule, delete the trap) instead of documenting around it |

When a rule keeps being violated despite being in the file, the fix is usually *not* more emphasis — it's either the file is too long (prune) or the rule needs to graduate to a hook.

## Mode: Create (bootstrapping a new file)

1. **Investigate before writing.** Read the package manifests and their scripts, CI config, lint/format config, Makefile/justfile, README, `.env.example`, and any existing instruction files (`.cursorrules`, `.github/copilot-instructions.md`, `GEMINI.md`, old CLAUDE.md) whose content should be consolidated. Note the test runner, the package manager, and anything *non-standard*.
2. **Verify every command you plan to include** by running it (or at minimum confirming the script exists in the manifest). A plausible-but-wrong command is worse than no command — the agent will trust it.
3. **Draft minimal.** Use the section skeleton in `references/template.md`. Resist the urge to showcase your investigation: most of what you learned is discoverable and therefore *excluded*. A first draft of 30–60 lines is a good sign; 200+ means you're transcribing the repo instead of distilling it.
4. **Set up cross-tool compatibility.** Make `AGENTS.md` the canonical file (it's the open standard read natively by Codex, Cursor, Copilot, Jules, Zed, and most others). For Claude Code, either symlink (`ln -s AGENTS.md CLAUDE.md`) or create a CLAUDE.md containing `@AGENTS.md` (the import form is preferred on Windows and when Claude-specific additions are needed). Details and the per-tool table are in `references/template.md`.
5. **Tell the user what you deliberately left out** and why (discoverable, enforced by tooling, etc.), so they can override if they know something you don't.

If the platform's built-in generator (e.g. `/init`) already produced a draft, treat it as raw material to prune hard — auto-generated files are exactly the kind the ETH study measured as net-negative.

## Mode: Update (the file lives alongside the code)

Update triggers — add or change a line when:

- The agent made the same mistake **twice** (once is noise; twice is a missing line).
- A human correction in review or chat keeps being re-typed across sessions.
- A change in this very PR adds/renames a command, env var, config schema, or architectural seam that agents must know. The instruction-file update belongs **in the same PR** as the change — that's the only reliable way to prevent drift.

When adding:

- **Check for conflicts** with existing rules first; contradictory instructions make the agent pick one arbitrarily.
- **Pay for the addition**: scan the file for a line that no longer earns its place and remove it. The budget is fixed; treat additions as trades.
- Place truly critical rules near the **top or bottom** of the file — middle-of-file instructions are the most weakly followed.
- Prefer positive framing ("Prefer X over Y because Z") over bare prohibitions ("Don't use Y") — negations are disproportionately dropped in long contexts. One short why-clause helps the agent judge edge cases; an essay spends budget. Reserve emphasis (IMPORTANT, **bold**) for the one or two rules that genuinely warrant it — emphasis inflation makes all of it invisible.

## Mode: Audit (periodic or on request)

Run this when asked to "review/clean up the CLAUDE.md", roughly quarterly, after a model upgrade, or whenever the agent seems to ignore the file. Work through the checklist; produce a proposed diff, not just findings.

1. **Stale commands** — for every command in the file, confirm the script/target still exists (cross-check package.json scripts, Makefile, CI). Run cheap ones to verify.
2. **Dead paths and pointers** — every referenced file, directory, and doc must exist. A file that says `src/db/` after the code moved to `src/data/` is actively harmful.
3. **Contradictions** — rules that conflict with each other or with current code reality.
4. **Discoverables** — content the agent would find anyway (directory layout, stack lists, things lint enforces). Cut.
5. **Obsolete-by-model-improvement** — rules added to babysit a weaker model that current models follow unprompted. Cut, restore only on evidence.
6. **Emphasis inflation and vague aspirations** — "write clean code"-grade lines and over-capitalization. Cut or sharpen into something verifiable.
7. **Length** — if the file is pushing past ~200 lines or ~50 distinct instructions, propose moving procedure-shaped content to linked docs/skills and path-specific content to nested files.
8. **Consolidation check** — duplicate instruction files for other tools (`.cursorrules`, etc.) that have drifted from the canonical file.

Report the diff with a one-line justification per removal, grouped by checklist category. Removals need more justification care than additions — the user may know why a weird line exists; flag suspected-but-unverified stale lines as questions rather than silently deleting.

## Monorepos

Place a lean root AGENTS.md for global defaults plus a per-package AGENTS.md for each subproject with its own toolchain. Agents use the **nearest file** (closest-wins, like .gitignore). Don't repeat root content in leaf files; leaf files hold only what differs. Note for Claude Code specifically: ancestor files load at launch, child-directory files load on demand when files there are read — so put always-needed content at the root and directory-specific content in the leaves.

## Reference files

- `references/template.md` — annotated section skeleton, a worked example, and the cross-tool compatibility table (which agent reads which file, symlink/import setup).
- `references/evidence.md` — the research behind every claim above, with sources. Read it when the user questions a recommendation or wants the "why".
