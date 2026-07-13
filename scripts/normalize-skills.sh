#!/usr/bin/env bash
#
# normalize-skills.sh — enforce this repo's skills layout. Idempotent; run anytime.
#
#   ~/.agents/skills/<name>/   canonical skill (real files, committed in this repo)
#   ~/.claude/skills/<name>    symlink -> ../../.agents/skills/<name>  (Claude Code's view)
#
# Why this exists: the Vercel `skills` CLI, when it detects it is running inside
# an agent (e.g. you ask Claude Code to run it), installs non-interactively by
# COPYING skills straight into ~/.claude/skills instead of symlinking. This
# script moves any such copies into the store and (re)creates the symlinks, so
# Claude Code always sees a single source of truth it can `git pull` to update.

set -euo pipefail

STORE="$HOME/.agents/skills"
CLAUDE="$HOME/.claude/skills"
mkdir -p "$STORE" "$CLAUDE"

moved=0 linked=0 pruned=0

# 1. Absorb stray real dirs (CLI copies) from ~/.claude/skills back into the store.
for path in "$CLAUDE"/*; do
  [ -e "$path" ] || continue          # no matches
  [ -L "$path" ] && continue          # already a symlink — leave it
  [ -d "$path" ] || continue          # ignore stray files
  name="$(basename "$path")"
  if [ -e "$STORE/$name" ]; then
    rm -rf "$path"                    # store already has it — drop the copy
  else
    mv "$path" "$STORE/$name"
    moved=$((moved + 1))
  fi
done

# 2. Ensure every real skill in the store is symlinked into ~/.claude/skills.
for path in "$STORE"/*; do
  [ -e "$path" ] || continue
  name="$(basename "$path")"
  [ -f "$path/SKILL.md" ] || continue   # only link actual skills, not workspaces
  want="../../.agents/skills/$name"
  if [ "$(readlink "$CLAUDE/$name" 2>/dev/null || true)" != "$want" ]; then
    ln -sfn "$want" "$CLAUDE/$name"
    linked=$((linked + 1))
  fi
done

# 3. Prune broken symlinks in ~/.claude/skills (skill removed from the store).
for path in "$CLAUDE"/*; do
  [ -L "$path" ] || continue
  [ -e "$path" ] || { rm -f "$path"; pruned=$((pruned + 1)); }
done

echo "normalize-skills: moved $moved copy(ies) into store, (re)linked $linked, pruned $pruned broken symlink(s)."
