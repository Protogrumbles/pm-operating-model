# Install — pm-operating-model

No build step, no dependencies beyond Python 3.8+ (standard library only).
Clone or copy this folder, then wire it into your tool of choice.

## Claude Code

**Option A — project plugin (recommended for a team):**

```bash
# From inside your project repo
mkdir -p .claude-plugin
cp -r /path/to/pm-operating-model .claude-plugin/
```

Then add the marketplace entry to `.claude-plugin/marketplace.json`, or
simply reference the skills by path — Claude Code picks up any
`SKILL.md` under `.claude-plugin/` automatically.

**Option B — personal skills directory:**

```bash
mkdir -p ~/.claude/skills
cp -r /path/to/pm-operating-model/skills/* ~/.claude/skills/
```

Restart Claude Code. Invoke a skill by name, e.g. "use the raci-generator
skill", or let Claude Code discover it from your prompt.

## Codex

Codex loads skills from `~/.codex/skills/` (or a project-local
`.codex/skills/`):

```bash
mkdir -p ~/.codex/skills
cp -r /path/to/pm-operating-model/skills/* ~/.codex/skills/
```

Verify with `codex --list-skills` (or check the skills panel in the
Codex app). The Python CLIs run as-is — no extra setup.

## Cursor

Cursor reads skills from `.cursor/skills/` in your project, or from a
global skills folder:

```bash
# Project-local (shared with the team via git)
mkdir -p .cursor/skills
cp -r /path/to/pm-operating-model/skills/* .cursor/skills/

# Global
mkdir -p ~/.cursor/skills
cp -r /path/to/pm-operating-model/skills/* ~/.cursor/skills/
```

Reference a skill in chat with `@raci-generator`, or let Cursor's agent
pick it up from context. Run the CLIs from the integrated terminal.

## Using the CLIs directly (any tool, or none)

Every script takes a JSON file (or stdin) and writes Markdown to stdout
unless `--md` / `--csv` output paths are given:

```bash
python3 skills/raci-generator/scripts/raci.py skills/raci-generator/examples/input.json
python3 skills/escalation-designer/scripts/escalation.py skills/escalation-designer/examples/input.json
python3 skills/okr-tracker/scripts/okr.py skills/okr-tracker/examples/input.json
python3 skills/adoption-telemetry/scripts/telemetry.py skills/adoption-telemetry/examples/input.json
```

Run `python3 <script> --help` for the full flag list. Example inputs live
in each skill's `examples/` folder; example outputs live in
`examples/output.*`.
