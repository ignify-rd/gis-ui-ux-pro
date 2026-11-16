# Research: how to write a Claude Agent Skill + package as plugin

Date: 2026-11-14. Sources:
- [BP] https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- [OV] https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- [CC] https://code.claude.com/docs/en/skills
- [SPEC] https://agentskills.io/specification
- [SC] https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- [BLOG] https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- [PLUG] https://code.claude.com/docs/en/plugins-reference
- [MKT] https://code.claude.com/docs/en/plugin-marketplaces
- [UUPM] https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

## 1. Folder layout

```
my-skill/
├── SKILL.md        # required: frontmatter + instructions
├── scripts/        # executable code; only the output enters context
├── references/     # docs read on demand
└── assets/         # files used in output (templates, icons, fonts)
```
- Use descriptive file names and group them by domain [BP][SPEC].
- Where Claude Code finds skills [CC]:
  - `~/.claude/skills/<name>/` for personal skills
  - `.claude/skills/<name>/` for project skills; this also works from parent dirs and nested subdirs
  - `<plugin>/skills/<name>/` for plugin skills, invoked as `/plugin:skill`
- If a name exists in more than one place, enterprise beats personal, and personal beats project.

## 2. Frontmatter

- `name` [OV][BP][SPEC]:
  - at most 64 chars
  - lowercase letters, digits and hyphens only
  - no leading/trailing hyphen and no `--`
  - must equal the dir name
  - no "anthropic" or "claude"
- `description` [OV][BP][SPEC]: at most 1024 chars, no XML tags. Say what the skill does and when to use it.
- Portable optional fields [SPEC]: `license`, `compatibility`, `metadata` (string map), `allowed-tools` (experimental).
- Claude Code adds more fields [CC]:
  - `when_to_use`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `model`, `effort`
  - `context: fork`, `paths`, `hooks`
  - description plus when_to_use is truncated at 1536 chars
- Uploading to claude.ai or the API with CC-only keys gives a hard error [CC].
- Placeholders [CC]: `$ARGUMENTS`, `${CLAUDE_SKILL_DIR}`, and `` !`cmd` ``.
- The frontmatter must start on line 1 [CC].

## 3. Progressive disclosure [OV][BLOG][BP]

Loading levels:
- Metadata is always loaded (~100 tokens).
- The body loads when the skill triggers. Keep it under 5k tokens and under 500 lines.
- Bundled files load only when read.

Rules:
- SKILL.md works as a table of contents.
- References go one level deep only.
- A reference file longer than 100 lines needs a TOC at its top.
- Use relative forward-slash paths.
- Say explicitly whether a file is to be run ("Run X") or read.
- In CC, after compaction only the first 5k tokens of an invoked skill are re-attached.

## 4. Best practices

Description:
- Write it in the third person, "Use when…", with concrete trigger terms.
- Be slightly "pushy", because skills under-trigger [SC].

Writing the body:
- Be concise; assume Claude is smart [BP].
- Match the degree of freedom to how fragile the task is: prose → pseudocode → exact command [BP].
- Give workflows and checklists Claude can copy, and use feedback loops: validate → fix → repeat [BP].
- Pick one default plus an escape hatch rather than a menu of options [BP].
- Avoid time-sensitive wording, and use consistent terminology [BP].
- Explain why instead of shouting ALWAYS/NEVER [SC].

Scripts:
- Scripts handle their own errors, justify their constants, and list their deps [BP].

Evals:
- Write evals before the docs:
  1. Run baseline tasks without the skill.
  2. Write 3 scenarios.
  3. Write the minimal instructions.
  4. Iterate with Claude A (author) and Claude B (user).
- For the description, use about 20 trigger queries (8–10 that should trigger, 8–10 near-miss negatives) [BP][SC].

## 5. Anti-patterns

- A vague or first-person description.
- A body over 500 lines.
- Nested references.
- Too many options.
- Windows backslash paths.
- Magic numbers.
- Not saying whether to run or read a script.
- Overfitting to test cases.
- CC-only keys in an uploaded skill.

## 6. Plugin packaging [PLUG][MKT]

```
plugin-root/
├── .claude-plugin/plugin.json        # only `name` is required (kebab-case); recommend version, description, author
├── .claude-plugin/marketplace.json   # name, owner{name}, plugins[{name, source}]
└── skills/<name>/SKILL.md            # default scan location
```
- The `skills` key in plugin.json adds extra dirs. They must start with `./`.
- Plugin names may not start with `claude-`, `anthropic-` or `cc-plugin-`.
- `..` is rejected in paths, because plugins are copied to a cache.
- `${CLAUDE_PLUGIN_ROOT}` is substituted inside SKILL.md but is NOT exported to Bash. `${CLAUDE_PLUGIN_DATA}` persists across updates.
- marketplace.json can use `"source": "./"`, so the repo root is both the marketplace and the plugin (this is how ui-ux-pro-max does it). If `strict:false` is set and a plugin.json exists, don't declare components in the entry.
- Install:
  1. `/plugin marketplace add owner/repo` (or a local dir)
  2. `/plugin install <plugin>@<marketplace>`
  3. `/reload-plugins`
- Validate with `claude plugin validate ./dir --strict`.

## 7. ui-ux-pro-max internals (local copy at .claude/skills/ui-ux-pro-max)

**SKILL.md** is 217 lines:
- A rule-category priority table.
- A query contract: one intent, 2–5 terms, retry once.
- Steps: analyze → `--design-system` → domain searches → `--stack` → pre-delivery checklist.

**data/** holds 12 domain CSVs (styles 89, colors 192, products 192, ui-reasoning 192, typography 74, ux-guidelines 120, charts 25, icons 105…) plus 22 stack CSVs.
- Columns in the guideline style: `No, Category, Guideline/Issue, Description, Do, Don't, Code Good, Code Bad, Severity, Docs URL`.

**scripts/core.py** is a stdlib-only BM25 search:
- k1=1.5, b=0.75.
- Normalizes text with stopwords and synonyms.
- Each domain has a minimum score floor.
- `detect_domain()` routes a query by keyword phrases.
- Indexes are cached.

**scripts/search.py** CLI flags:
- `query`, `-d/--domain`, `-s/--stack`, `-n` (1–20, default 3)
- `--json`, `--full`
- `-ds/--design-system`, `-p`, `-f ascii|markdown`, `--persist`, `-o`, `--page`

Output is markdown, `### Result N` per hit. With no hits it prints "No matches" plus the nearest terms.

**Other scripts:**
- `design_system.py` combines product, style, color, landing and typography results into one design-system box.
- `reasoning_contract.py` defines a closed JSON grammar of decision rules: data is never executed.

**Tests** are unittest, 15 modules, with relevance fixtures.

**Known bugs in the copied version:**
- SKILL.md calls the script through `${CLAUDE_PLUGIN_ROOT}/.claude/skills/...`, which breaks when the skill is installed as a project skill.
- 4 test modules fail outside the upstream repo because of `REPO = next(...)`.
