# AGENTS.md template and cross-tool setup

## Section skeleton

No section is mandatory — the AGENTS.md standard is plain Markdown with no required schema. Use only the sections the repo actually needs; an empty section is a section to delete. The skeleton below is ordered so the most-followed positions (top and bottom) hold the highest-stakes content.

```markdown
# <Project> — Agent Guide

One sentence: what this is. Link README for product scope, ARCHITECTURE.md for system shape.

## Stack
Only the non-guessable: runtime version constraints, unusual module settings
(e.g. "ESM with .ts import extensions"), the package manager if not npm,
config/secret locations.

## Commands
The exact invocations for typecheck, lint, test (whole suite AND single file),
build, run. Verified, not transcribed. If a command needs a flag for a
non-obvious reason, one why-clause.

## Layout
ONLY if the structure is non-obvious or carries rules ("core/ never imports
adapters/"). A plain directory listing is discoverable — omit it.

## Code style
Only deviations from defaults and things the linter does NOT enforce.

## Testing
Where tests live, what kind is expected with a change, fakes vs mocks policy.

## Boundaries
The highest-stakes section — keep it near the end (well-followed position).
Always / Ask first / Never groupings work well:
- Always: invariants to maintain (read ADRs before architectural changes).
- Ask first: actions needing human sign-off (new dependency, schema change).
- Never: hard lines (commit secrets, bypass auth checks).
```

Optional sections when warranted: dev-environment quirks (required env vars, auth refresh procedures), PR/commit etiquette (only if non-standard — e.g. Conventional Commits feeding semantic-release), release process (the two facts an agent needs, linking the full doc).

## Worked example (a strong real-world file, condensed)

Note what it does: every command is exact and runnable; layout appears only because it carries a rule; style rules are only the non-defaults; boundaries are grouped by severity; procedures live elsewhere and are linked.

```markdown
# Acme Bot — Agent Guide

Internal Slack bot. Product scope: `README.md`. System diagram: `docs/ARCHITECTURE.md`.

## Stack
- Node 24, ESM, strict TypeScript. Native type stripping, so imports use `.ts` extensions.
- YAML configs in `config/`; secrets in env (see `.env.example`).

## Commands
- `npm run typecheck`
- `npm test` — single file: `npx vitest run path/to/foo.test.ts`
- `npm start` — boot the bot (reads `.env`)

## Layout
- `src/core/` — pure domain. **Never imports from `src/adapters/`.**
- `src/adapters/` — the swap seams only.
- Unit tests colocate (`foo.ts` ↔ `foo.test.ts`); `tests/` is integration only.

## Code style
- Functions over classes unless state demands otherwise.
- Above every module-scope function, one short comment on why it exists.

## Boundaries
**Always**: read `docs/adr/` before architectural changes; validate configs
through zod at boot.
**Ask first**: new runtime dependency; loosening a zod schema.
**Never**: commit secrets; bypass the `employees.yaml` allowlist.
```

## Cross-tool compatibility

**Canonical file: `AGENTS.md`.** It is the open standard (launched by OpenAI in 2025, now under the Linux Foundation's Agentic AI Foundation) and is read natively by the widest set of tools.

| Tool | Reads natively | Setup if not native |
|---|---|---|
| OpenAI Codex | AGENTS.md | — |
| Cursor | AGENTS.md (`.cursorrules` is deprecated; `.cursor/rules/*.mdc` for path-scoped) | — |
| GitHub Copilot coding agent | AGENTS.md (nested supported); `.github/copilot-instructions.md` ranks higher | — |
| Google Jules | AGENTS.md | — |
| Zed, Windsurf, Devin, Aider*, goose, Amp, JetBrains Junie, Warp, Factory, RooCode | AGENTS.md | *Aider: `read: AGENTS.md` in `.aider.conf.yml` |
| **Claude Code** | CLAUDE.md only | Symlink `ln -s AGENTS.md CLAUDE.md`, **or** a CLAUDE.md containing `@AGENTS.md` plus any Claude-specific additions. Prefer the import form on Windows (symlinks need Dev Mode) or when Claude-only content exists. |
| Gemini CLI | GEMINI.md by default | Add `"context": {"fileName": ["AGENTS.md"]}` to `.gemini/settings.json`, or symlink. |

When consolidating: migrate content from legacy files (`.cursorrules`, `.windsurfrules`, old tool-specific files) into AGENTS.md, then delete or symlink the originals so there is one source of truth. Drifted duplicates are a top source of contradictory instructions.

### Precedence rules (all tools, roughly universal)

1. Explicit user chat prompt — overrides everything.
2. Nearest AGENTS.md to the files being edited (closest-wins, like `.gitignore`).
3. Root AGENTS.md.
4. User/org-level instruction files.

### Claude Code loading specifics

- Ancestor-directory CLAUDE.md files load in full at launch (root → cwd order); **subdirectory** files load on demand when files there are read.
- `@path` imports load at launch too (max depth 4) — splitting a long file into imports organizes it but does **not** save context. Only path-scoped rules (`.claude/rules/` with `paths:` frontmatter), subdirectory files, and skills are truly lazy-loaded.
- `CLAUDE.local.md` (gitignored) holds personal-machine notes; don't put team content there.
