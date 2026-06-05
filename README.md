# What I feed the robots

One version-controlled home (`~/.agents/skills/`) for all agent skills — both ones I write and ones installed from the [skills CLI](https://skills.sh). Claude Code picks everything up globally via symlinks in `~/.claude/skills/`.

## How it's wired

```
~/.agents/skills/<name>/SKILL.md     <- actual skill content lives here (this repo)
~/.claude/skills/<name>              <- symlink pointing back to ../../.agents/skills/<name>
.skill-lock.json                     <- tracks which skills the CLI manages (don't edit by hand)
```

The CLI only touches skills listed in `.skill-lock.json`. Anything not in the lockfile is mine — `skills update` / `skills remove` will never disturb it.

## Installing a skill from the CLI

```sh
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser
```

Then select **claude-code**, **global**, **sym-link**. (At the time of writing there's a bug with the `-g` flag.)

This installs into `~/.agents/skills/<name>` and creates the `~/.claude/skills/<name>` symlink automatically. Commit the new directory plus the updated `.skill-lock.json`.

## Writing my own skill

```sh
cd ~/.agents/skills
npx skills init my-skill                                      # scaffolds my-skill/SKILL.md
ln -s ../../.agents/skills/my-skill ~/.claude/skills/my-skill # make Claude Code see it globally
```

Then edit `my-skill/SKILL.md` — the frontmatter `name:` and `description:` are what trigger it. Commit when happy. New Claude Code sessions pick it up automatically.

Rules for custom skills:

- Don't reuse a name that a CLI-managed skill has (or might want) — `skills add` would prompt to overwrite and the lockfile would claim ownership.
- Don't add custom skills to `.skill-lock.json` — staying out of it is what protects them.

## Maintenance

| Task | Command |
|---|---|
| Update CLI-managed skills | `npx skills update` (then commit changes) |
| Remove a CLI-managed skill | `npx skills remove <name>` (cleans up the symlink too) |
| Remove a custom skill | `rm -r ~/.agents/skills/<name> ~/.claude/skills/<name>` |
| List what the CLI manages | `npx skills ls` |
| Restore on a new machine | clone this repo to `~/.agents`, then re-create the symlinks (see below) |

### New machine setup

```sh
git clone <this repo> ~/.agents
mkdir -p ~/.claude/skills
for d in ~/.agents/skills/*/; do
  ln -sfn "../../.agents/skills/$(basename "$d")" ~/.claude/skills/"$(basename "$d")"
done
```
