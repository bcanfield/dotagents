# Evidence behind the recommendations

Research digest, compiled June 2026. Cite these when the user asks why a recommendation holds.

## Instruction budget and length

- **IFScale benchmark** (arXiv 2507.11538): best frontier models hit only 68% adherence at 500 simultaneous instructions; degradation starts well before and is roughly linear for frontier models. Failure mode is **omission** (silently dropping rules), not misinterpretation. Earlier-in-prompt instructions are favored. Practitioner translation: ~150–200 reliably-followed instructions total, of which the agent's system prompt consumes ~50 — leaving ~100–150 for the instruction file.
- **HumanLayer** (humanlayer.dev/blog/writing-a-good-claude-md): adherence degrades **uniformly across the whole file** as instruction count grows — each addition weakens every existing rule. <300 lines acceptable, <60 excellent.
- **TianPan 2,500-repo corpus analysis** (tianpan.co, Feb 2026): top-performing files averaged 300–350 words; >500 words diminishing returns; >1,000 words correlated negatively.
- **Anthropic docs** (code.claude.com/docs/en/memory, /best-practices): target under 200 lines; "Bloated CLAUDE.md files cause Claude to ignore your actual instructions."

## Do these files even help?

- **ETH Zurich + LogicStar, "Evaluating AGENTS.md"** (arXiv 2602.11988, Feb 2026). 138 tasks across 12 repos with real developer-written context files, plus SWE-bench Lite; Claude Code, Codex, Qwen Code. Findings:
  - Developer-written files: **+4% success** on average, at up to +19% inference cost.
  - **LLM-generated files: net negative** — worse success in 5 of 8 settings (−0.5 to −2%), +20–23% cost, more steps. They were "highly redundant with existing repo documentation" (95–100% contained codebase overviews).
  - **Codebase overviews measured useless**: no faster discovery of the first relevant file.
  - Agents follow the files *too* well: tools mentioned in the file get used 1.6× more (repo-specific tools 2.5×) — so stale or irrelevant content actively anchors behavior.
  - Paper's recommendation: files should contain "only minimal requirements" — repo-specific build/test commands and non-obvious tooling.
- **Efficiency study** (arXiv 2601.20404, Jan 2026): 124 paired PR tasks, with vs. without real AGENTS.md; with the file, median output tokens −16.6% and wall-clock −28.6%. The two papers agree: command/structure info cuts wasted exploration; everything beyond that adds cost without adding success.

## Writing style

- **Position effects**: IFScale found bias toward early instructions; practitioners report beginning and end are strongest, middle weakest — moving a chronically-ignored rule to the end of the file is a documented fix (shareuhack.com 2026 guide; HumanLayer).
- **Negations**: "Do not X" rules are disproportionately dropped in long contexts; rephrase as "Prefer X over Y" (builder.io; community consensus).
- **Emphasis**: Anthropic officially endorses tuning with emphasis ("IMPORTANT", "YOU MUST"), but it only works when scarce. For 100%-required rules, use hooks — instruction files are advisory, hooks are deterministic (Anthropic best-practices).
- **Why agents break rules they've read** (yajin.org post-mortem, Mar 2026): (1) under rapid-fire requests the model prioritizes the immediate task over file rules; (2) context compaction preserves objectives but drops process standards; (3) the model treats rules as priors and probabilistically grants itself exceptions. Mitigation: compress to a few non-negotiables + hooks for enforcement. A short rationale clause helps the model judge when a rule applies; essays spend budget.
- **Examples beat abstractions**: point at a real file embodying a pattern ("`HotDogWidget.php` is a good example") and use `file:line` pointers instead of pasted snippets, which go stale (builder.io; HumanLayer).
- **Delivery diagnostic**: paste a chronically-ignored rule directly into the first user message; if it's followed there but not from the file, the file is too long/diluted — prune or convert to a hook (shareuhack.com).

## Lifecycle

- **Anthropic, verbatim**: "Treat it like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts."
- **Update triggers** (Anthropic memory docs): same mistake twice; review catches something the agent should have known; re-typing the same correction across sessions; a new teammate would need the context.
- **Prune triggers** (TianPan; aicodex.to maintenance guide): rules a linter now enforces; rules current models follow unprompted (re-test on model upgrades); rules untested in the past month; ~quarterly line-by-line audit; architecture changes update the file **in the same PR**.
- **Escalation ladder** (Anthropic): advisory rule → emphasized rule → hook (deterministic) → skill/slash command for on-demand procedures.
- **Bootstrap caution**: Anthropic recommends `/init` as a starter draft; HumanLayer says don't auto-generate at all; the ETH data sides with HumanLayer (LLM-generated files measured net-negative). Resolution: generated output is raw material to prune hard, never a finished file.
- **Fix the codebase first** (Addy Osmani, addyosmani.com/blog/agents-md): the file is "a living document of friction you haven't fixed yet" — when agents struggle repeatedly, prefer adding the lint rule / test / restructure over adding instructions; expect instruction lifespan to shorten as models improve.

## The standard and ecosystem

- **agents.md**: plain Markdown, no required fields or schema; "a README for agents." Originally OpenAI/Sourcegraph/Google/Cursor/Factory collaboration, donated to the Linux Foundation's Agentic AI Foundation (Dec 2025); 60k+ repos.
- **Monorepos**: nearest-file-wins precedence; OpenAI's own monorepo has 88 AGENTS.md files. Explicit user prompts override all files.
- **Test-command behavior**: agents attempt to execute commands listed in the file and fix failures before finishing — another reason every listed command must actually work.
- **Claude Code interop** (code.claude.com/docs/en/memory): reads CLAUDE.md, not AGENTS.md; official options are a symlink or a CLAUDE.md containing `@AGENTS.md`. `/init` incorporates an existing AGENTS.md and also reads `.cursorrules`, `.windsurfrules`, `.devin/rules/`.

## Source URLs

- https://agents.md
- https://arxiv.org/abs/2602.11988 (ETH Zurich, "Evaluating AGENTS.md")
- https://arxiv.org/html/2601.20404v2 (efficiency study)
- https://arxiv.org/pdf/2507.11538 (IFScale)
- https://code.claude.com/docs/en/memory and https://code.claude.com/docs/en/best-practices
- https://www.humanlayer.dev/blog/writing-a-good-claude-md
- https://tianpan.co/blog/2026-02-14-writing-effective-agent-instruction-files
- https://addyosmani.com/blog/agents-md/
- https://www.builder.io/blog/claude-md-guide and https://www.builder.io/blog/agents-md
- https://www.aicodex.to/articles/claude-md-maintenance
- https://yajin.org/blog/2026-03-22-why-ai-agents-break-rules/
- https://www.shareuhack.com/en/posts/claude-code-claude-md-setup-guide-2026
