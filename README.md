# What I feed the robots

Agent skills live in `skills/` here. Some I write, some come from the [skills cli](https://skills.sh). Claude Code finds them all through symlinks in `~/.claude/skills/`.

<details>
<summary>How it fits together</summary>

```
~/.agents/skills/<name>/SKILL.md    actual skill, lives in this repo
~/.claude/skills/<name>             symlink pointing back at the line above
.skill-lock.json                    what the cli owns. don't hand-edit
```

The cli only touches skills listed in the lockfile, so my own skills are safe from `skills update` / `skills remove` as long as I keep them out of it.

</details>

<details>
<summary>Installing from the cli</summary>

```
npx skills add https://github.com/vercel-labs/agent-browser --skill agent-browser
```

Then select claude-code, global, sym-link. At the time of writing this there's a bug with the `-g` flag. It installs into `skills/` and makes the symlink for me. Commit the new folder plus `.skill-lock.json`.

</details>

<details>
<summary>Writing my own</summary>

```
cd ~/.agents/skills
npx skills init my-skill
ln -s ../../.agents/skills/my-skill ~/.claude/skills/my-skill
```

The `name:` and `description:` frontmatter in SKILL.md is what makes it trigger. New Claude Code sessions pick it up automatically. Commit when happy.

Two things to avoid: don't name a skill the same as something the cli installed (`skills add` will offer to overwrite it), and don't add my own skills to the lockfile.

</details>

<details>
<summary>Maintenance</summary>

- `npx skills update` updates cli-managed skills, then commit
- `npx skills remove <name>` also cleans up the symlink
- removing one of mine: `rm -r ~/.agents/skills/<name> ~/.claude/skills/<name>`
- `npx skills ls` shows what the cli thinks it owns

</details>

<details>
<summary>New machine</summary>

```sh
git clone <this repo> ~/.agents
mkdir -p ~/.claude/skills
for d in ~/.agents/skills/*/; do
  ln -sfn "../../.agents/skills/$(basename "$d")" ~/.claude/skills/"$(basename "$d")"
done
```

</details>
