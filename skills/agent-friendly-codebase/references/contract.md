# The contract: AGENTS.md, unit docs, scoped rules

## Contents

1. What goes where
2. AGENTS.md template
3. The verification section
4. Unit doc template
5. The feature map
6. Scoped rules and tool pointers
7. Worked example doc

## 1. What goes where

| Information                                              | Lives in                                   | Kept true by                          |
| -------------------------------------------------------- | ------------------------------------------ | ------------------------------------- |
| Layout, dependency rules, anatomy, how to verify         | AGENTS.md (always loaded, short)           | the checker; review                   |
| What a unit does, as a user would see it                 | that unit's doc                            | the review skill                      |
| Which units, blocks and core modules exist, one line each, and what users call them | the feature map (`FEATURE_MAP.md`) | the checker (`feature-map` rule); review for "Also called" |
| Which files a unit has, one line each                    | the unit doc's `## Files`                  | the checker (`unit-files` rule)       |
| Rules for some paths only (tests, migrations, one package) | scoped rule files                        | the review skill                      |
| Who depends on whom; who owns a file                     | nowhere: `graph`, `owner`                  | computed                              |
| Counts (tests, files, suppressions, units)               | nowhere: commands print them               | computed                              |
| Why a line is suppressed                                 | inline, on the suppression                 | the checker (`suppressions` rule)     |
| Why a tool is configured a certain way                   | a comment in that config file              | review                                |
| Tooling quirks with no config line to sit on             | AGENTS.md "Tooling notes"                  | review                                |

AGENTS.md is read on every task, so every line costs context on every task.
Leave out of it:

- counts of anything
- inventories that the tree or a script can produce
- behaviour descriptions, which belong in unit docs
- path-specific rules, which belong in scoped rule files
- detailed restatements of what a tool already enforces (one line plus the
  name of the check is enough)

## 2. AGENTS.md template

Fill this in from the audit, and delete any section that doesn't apply. Aim
for under ~150 lines. Write every command as its literal invocation
(`npm run check:unit -- channels`, `just check-unit orders`), not as a role
name.

````markdown
# AGENTS.md

<One paragraph: what this is; units live in <dir>, shared code in <dir>; a
change is done when `<check>` is green (see Verification).>

## Layout

<tree with one line per top-level directory; no per-file lists>

## Dependency rules

| Layer | May import |
| ----- | ---------- |

- Other units only through their public surface (`<surface file>`).
- No cycles between units; when one appears, move the shared piece to `<core>`.
- Promote to `<building blocks>` only on second use.

Enforced by `<structure>`. Use `<graph> <unit>` for a unit's dependencies,
`<graph> <unit> --reverse` for its dependents, and `<owner> <file>` to find the
owning unit and its doc.

## Unit anatomy

<the unit template tree: public surface, main files, tests, unit doc; plus a
server-only folder if client and server code share this tree>

- Tests: <placement rule; which suffix or directory belongs to which runner>.
- Unit doc: observable behaviour by sub-feature, ending with `## Files`.
- [FEATURE_MAP.md](FEATURE_MAP.md): which unit owns what, and what shared code
  already exists. Start there to find where a change goes, and check it before
  writing a helper.

## Conventions

Each one names the check that enforces it, or says "review" if only the
review skill checks it.

- Comments in source files: <policy>. Explanations go in the unit doc or a test
  name. — `<structure>`
- Suppressions: single line, with an inline reason. — `<structure>`
- Formatting: never by hand; run `<fix>`. — `<format-check>`
- <repo-specific conventions approved in the report> — <check or "review">
- Scoped rules: <each scoped rule file, and what it covers>

## Verification

<see section 3 of this file>

## Running locally

<`<dev-local>` and what it starts; how ports, databases and build directories
are isolated per worktree; which flows need real keys>

Environment: run `<env-check>` (or list only variables whose purpose isn't
obvious from their names).

## Adding or changing a unit

1. Find the owning unit in FEATURE_MAP.md and read its unit doc. For a new
   unit, run `<new-kind> <name> "<one sentence: what a user can do>"`, which
   also adds its feature-map row.
2. Describe the behaviour change in the unit doc.
3. Write or adjust the test at the right level.
4. Implement inside the unit; export new public pieces from the surface file.
5. Iterate with `<check-unit> <unit>`.
6. If the unit's scope changed, update the first line of its doc (the checker
   makes you update its feature-map row to match), and add any new name users
   call it to "Also called".
7. Run `<fix>`, then `<check>`, plus `<e2e>` if a user flow changed.
8. Self-review the diff with the `<repo>-review` skill, and fix what it finds.

See <worked example path> for a real change, end to end.

## Scripts

<only commands not already in the Verification table: seed/reset, inspect,
env-check, graph, owner, test-coverage. One line each: command — what it does
— when to run it.>

## Tooling notes

<only quirks that have no config line to sit on>
````

If the team uses a tool that doesn't read AGENTS.md natively, add a pointer to
it rather than a copy (section 6).

## 3. The verification section

This section lets an agent prove a change is correct *and* complete without
asking anyone. Adapt it to the repo's actual commands, and drop rows that
don't exist (e2e, build, dev-local).

**Definition of done**: state it in exactly these words: "A change is not done
until `<check>` is green, `<e2e>` is green if any user flow changed, and every
item in the completeness checklist is ticked."

**Commands**:

| Command           | Proves                                                           | When                                   |
| ----------------- | ---------------------------------------------------------------- | -------------------------------------- |
| `<typecheck>`     | types hold across the whole project                              | after each series of edits             |
| `<lint>`          | framework and correctness rules, with zero warnings              | after each series of edits             |
| `<structure>`     | layers, public surfaces, cycles, anatomy, test placement, docs, suppressions, sync | after adding or moving files |
| `<format-check>`  | every file is formatted                                          | before declaring done                  |
| `<test-baseline>` | all tests pass and none were lost                                | before declaring done                  |
| `<check-unit> <unit>` | all of the above for one unit, in seconds                    | while iterating                        |
| `<check>`         | all of the above for the whole repo                              | before declaring done                  |
| `<fix>`           | formats and autofixes                                            | before `<check>`                       |
| `<e2e>`           | real user flows against a local backend, with no keys            | after touching any user flow           |
| `<check-all>`     | `<check>` + e2e                                                  | restructures, multi-unit changes       |
| `<build>`         | the production build succeeds                                    | after changing routing, config or deps |

**While iterating**: `<check-unit> <unit>`, `<test runner> <path>`,
`<e2e runner> <path>`.

**Completeness checklist** (correct is not the same as complete). This block is
the canonical copy: the review skill and the bot configs carry synced copies.
List only what `<check>` can't verify.

```markdown
<!-- sync:completeness:start -->
- [ ] New behaviour has a test at the right level (<helper → unit test;
      component → component test; user flow → e2e>), and the test would fail if
      the behaviour broke. A new branch with no test isn't complete.
- [ ] The owning unit doc describes the new or changed behaviour. If the unit's
      scope changed, its first line (and so its feature-map row) still says
      what a user can do, and any new name users call it is in "Also called".
- [ ] New public pieces are exported from the public surface; internals are not.
- [ ] If a route, script or rule changed, AGENTS.md says so.
- [ ] No test was deleted, skipped or weakened without a reason in the PR.
- [ ] Every new suppression's reason holds up.
<!-- sync:completeness:end -->
```

**When something fails**:

- **Structure check**: the message names the file, line, rule and fix. Fix the
  structure; never widen the rule.
- **Baseline**: fewer tests means you deleted a test or broke test discovery.
  Restore it, or lower the baseline by hand *and say so in the PR*. "Stale" in
  CI means the count rose: run `<test-baseline>` locally and commit the file. On
  a merge conflict in the baseline file, take the larger numbers and rerun.
- **E2E**: open the runner's failure artefacts (traces, screenshots, logs)
  before changing any code, then rerun the single spec. Flows that need real
  keys skip locally and are listed below.
- **Lint**: fix the code. A single-line suppression with an inline reason is a
  last resort.
- **A gate seems wrong**: say so in the PR. Don't edit checker rules, lint
  config, the baseline or CI to get to green.

**Cannot be verified locally**: list production-only flows, paid or
third-party APIs, which specs skip locally, and the exact command that runs
them with real keys. Agents report these rather than building workarounds.

## 4. Unit doc template

Name it FEATURE.md or README.md, whichever the user chose; use one name
everywhere.

```markdown
# <Unit name>

<One sentence: what a user can do with it. The same sentence is the unit's
row in FEATURE_MAP.md, and the checker compares them.>

## <Sub-feature>

- <Observable behaviour, as a user would describe it.>
- <Edge behaviour: what happens when empty, offline, unauthorised…>

## Files

- `<file>`: <one-line purpose>
- `tests/<file>`: <what it covers>
```

Describe behaviour, not implementation. Never include counts or constants
copied from the code: they drift, and the code is the source of truth for
them. The `## Files` list is the one file list that's allowed, because each
line adds a purpose and the checker keeps it complete. Parallel agents each
edit their own unit's doc, so these docs don't become hotspots.

## 5. The feature map

`FEATURE_MAP.md` sits next to AGENTS.md. It's the routing table from a request
in the user's words ("make reactions work in threads") to the folder and doc
that own it. Agents open it to answer three questions:

- Which unit owns this behaviour?
- Does a helper for this already exist?
- Where do I start reading?

`<owner> <path>` answers the reverse question (file → unit), so the map never
lists files.

**Name and loading.** Use `FEATURE_MAP.md` unless "feature" reads oddly for the
repo (a library or a backend might use `MODULE_MAP.md`); settle it in Phase 2
with the unit doc name. AGENTS.md *links* to it, and doesn't import it (no
`@FEATURE_MAP.md` in `CLAUDE.md`), so it costs context only when an agent is
locating something.

### Template

Rename the tables to the layers chosen in Phase 1, and drop tables for layers
the repo doesn't have. Within each table, sort the rows alphabetically. Two
agents adding units then insert rows in different places instead of both
appending at the end, so merge conflicts are rarer.

```markdown
# Feature map

Find the unit that owns a behaviour here, then read its FEATURE.md before
changing anything. The rules are in [AGENTS.md](AGENTS.md). To find the unit
that owns a file, run `<owner> <path>`.

## Features

| Feature | What a user can do | Also called |
| ------- | ------------------ | ----------- |
| [channels](features/channels/FEATURE.md) | Create, browse, join and leave channels. | rooms |
| [reactions](features/reactions/FEATURE.md) | React to a message with an emoji and see who reacted. | emoji, likes |

## Views

| View | Where it appears |
| ---- | ---------------- |
| [sidebar](views/sidebar/FEATURE.md) | Left column: workspace switcher, channel list and DMs. |

## Primitives

| Primitive | Use it for |
| --------- | ---------- |
| [avatar](primitives/avatar.tsx) | A user's picture, with a presence dot and initials as the fallback. |

## Shared code

| Module | Reach for it when |
| ------ | ----------------- |
| [ids](lib/ids.ts) | You need a room, thread or message id. Never build one by hand. |

## Cross-cutting

- Data model: <where it's defined, in one line>.
- API routes: each `app/api/<name>/route.ts` re-exports one handler from
  `features/<unit>/api/`. Run `<owner>` on a route file to find its unit.
- <Anything else no unit owns, one line each: auth model, realtime model…>

## Not yet migrated

| Legacy path | Moving to |
| ----------- | --------- |
| `components/search/` | `features/search` |
```

### What each column is for

- **What a user can do**: the one sentence from Phase 1 that passed the unit
  test ("can you describe it in one sentence a user would understand?"). It's
  also the first line of the unit's doc, word for word, and the checker
  compares the two. So the behaviour is described in one place, and the map
  can't drift from it.
- **Also called**: the other words users, the UI, issues and the team use for
  it ("DMs" for `conversations`, "workspace" for `organizations`). Collect them
  from UI copy, route names, issue titles and the README. This column is what
  makes the map worth having: it's the one thing the tree can't tell an agent.
  Leave it empty when there are no other names.
- **Where it appears** (composition): the region of the screen, or the step of
  the flow, so an agent can go from "the thing on the left" to a folder.
- **Use it for / Reach for it when** (building blocks and core): written from
  how callers use the module, not from its export names. These rows are what
  stop agents writing a second `formatDate`.
- **Cross-cutting**: one line per pattern, never a list of instances. Say how
  API routes map to units; don't list the routes.
- **Not yet migrated**: only during an incremental migration. It tells agents
  where legacy code lives, and where it's going. Delete the section once it's
  empty.

### What never goes in it

- file lists (they belong in the unit doc's `## Files`)
- dependencies between units (`<graph>` prints them)
- counts of anything
- behaviour beyond the one sentence (it belongs in the unit doc)
- status, owners, roadmap or ticket links (they go stale, and they aren't
  needed to make a change)

### When to write it

| Situation | When |
| --------- | ---- |
| Big-bang migration | After the last checkpoint, together with the unit docs. The Phase 2 unit map is the draft: its "What a user can do" column becomes the summaries. |
| Incremental migration | In the first PR, listing the units that already exist and a "Not yet migrated" table. Each migration PR moves one row from that table into the right one. |
| An existing map | During the drift audit: remove dependency columns, file lists, counts and status; add "Also called"; put it under the checker. |
| A tiny repo (a handful of units, no building blocks) | Skip the separate file. Put the features table in AGENTS.md. |

### Size

Aim for under ~100 lines. When there are too many units for that, group the
features table under subheadings by product area. In a monorepo, write one map
per package, next to that package's AGENTS.md. The root map then lists only
the packages, each with a one-line summary and a link to the package's map.

### Keeping it true

- The checker's `feature-map` rule (`checks-and-scripts.md`) fails when:
  - a unit, composition piece, building block or core module has no row, or
    has more than one
  - a link doesn't resolve
  - a unit's summary differs from the first line of its doc
  - rows aren't sorted
  - the "Not yet migrated" table and the checker's legacy-directory config
    disagree
- The scaffolder takes the one-sentence summary as an argument. It writes the
  sentence as the first line of the new unit's doc, and inserts the row into
  the map in sorted position. So a freshly scaffolded unit passes `check`.
- Other edits are by hand. Renaming or splitting a unit updates its row in the
  same PR, and the checker fails until it does.
- The "Also called" column isn't checked by a script. The review skill flags a
  PR that introduces a new user-facing name without adding it.

## 6. Scoped rules and tool pointers

Rules that matter only for some files go where agents load them only when
they're working on those files. Examples: e2e locator rules, how to use the
test backend mock, migration rules, one package's quirks. This keeps the
always-on contract short.

| Mechanism                                  | Read by (check current docs)                                       |
| ------------------------------------------ | ------------------------------------------------------------------ |
| Root `AGENTS.md`                           | Codex, Cursor, GitHub Copilot (coding agent and code review), and many others |
| Nested `AGENTS.md` in a subfolder (the nearest one applies) | Codex, Cursor, and others                         |
| `CLAUDE.md` (root and nested)              | Claude Code, which doesn't read AGENTS.md: put `@AGENTS.md` in the root `CLAUDE.md` to import it |
| `.claude/rules/*.md` with `paths:` frontmatter | Claude Code (glob-scoped)                                      |
| `.cursor/rules/*.mdc` with `globs:`        | Cursor (glob-scoped)                                               |
| `.github/instructions/*.instructions.md` with `applyTo:` | GitHub Copilot (glob-scoped)                         |

- **Keep one source of truth.** When a rule applies to one folder, a nested
  AGENTS.md is the most portable choice (add a nested `CLAUDE.md` containing
  `@AGENTS.md` if Claude Code is used). When a rule applies to a glob that spans
  folders (`**/*.spec.ts`), write it once in the primary tool's glob mechanism.
  Give other tools a copy between `sync` markers, which the checker compares.
- **Point, don't copy**, for always-on files: a `CLAUDE.md` containing
  `@AGENTS.md` (plus any Claude-specific additions) rather than a second
  contract.

## 7. Worked example doc

Write this as `docs/EXAMPLE_CHANGE.md`, or as a short AGENTS.md section.
Agents pattern-match on it, and reviewers can point to it.

- **Preferred**: the first unit-sized change made after the restructure, so
  every path in it is real.
- **Otherwise**: a representative change from history (new behaviour inside
  one capability, with tests and docs). Rewrite its paths through the
  migration's move map, and say that you rewrote them.
- **Never invent one.** If neither exists yet, list it as a follow-up.

```markdown
# Worked example: <change>

Commit(s): <sha> — <one line>. Chosen because <it touched one unit end to end>.

## Order of work
1. Unit doc: described the new behaviour (`<path>`)
2. Model or logic: `<path>`: <what changed>
3. Test: `<path>`: <what it asserts>
4. UI or handler: `<path>`
5. Public surface: exported `<name>` from `<surface file>`
6. E2E: `<path>`

## Commands
`<check-unit> <unit>` (caught: <…>), `<fix>`, `<check>`, `<e2e> <path>`

## What review caught that the checks didn't
<…, or "nothing">
```
