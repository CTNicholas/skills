# The contract: AGENTS.md, FEATURE_MAP.md, FEATURE.md

## Contents

1. What goes where
2. AGENTS.md template
3. The verification section
4. FEATURE.md template
5. FEATURE_MAP.md
6. Nested rules
7. Worked example doc

## 1. What goes where

| Information | Lives in | Kept true by |
| --- | --- | --- |
| Layout, dependency rules, anatomy, how to verify | `AGENTS.md` (read on every task, short) | the checker; review |
| Which features, blocks and core modules exist, one line each, and what users call them | `FEATURE_MAP.md` (a separate file next to AGENTS.md) | the checker (`feature-map` rule); review for "Also called" |
| What a feature does, as a user would see it | that feature's `FEATURE.md` | the review skill |
| Which files a feature has, one line each | `FEATURE.md`'s `## Files` section | the checker (`feature-files` rule) |
| Rules for some paths only (tests, migrations, one package) | a nested `AGENTS.md` in that folder | the review skill |
| Who depends on whom; who owns a file | nowhere: `graph`, `owner` | computed |
| Counts (tests, files, suppressions, features) | nowhere: commands print them | computed |
| Why a line is suppressed | inline, on the suppression | the checker (`suppressions` rule) |
| Why a tool is configured a certain way | a comment in that config file | review |
| Tooling quirks with no config line to sit on | AGENTS.md "Tooling notes" | review |

There's no `CLAUDE.md`: agents read `AGENTS.md`. If the repo has a `CLAUDE.md`,
move anything still true into AGENTS.md and delete it, so there's one contract.

AGENTS.md is read on every task, so every line costs context on every task.
Leave out of it:

- counts of anything
- inventories that the tree or a script can produce (the feature list lives in
  FEATURE_MAP.md)
- behaviour descriptions, which belong in `FEATURE.md`
- path-specific rules, which belong in nested AGENTS.md files
- detailed restatements of what a tool already enforces (one line plus the
  name of the check is enough)

## 2. AGENTS.md template

Fill this in from the audit, and delete any section that doesn't apply. Aim
for under ~150 lines. Write every command as its literal invocation
(`npm run check:feature -- channels`, `just check-feature orders`), not as a
role name.

````markdown
# AGENTS.md

<One paragraph: what this is; features live in <dir>, shared code in <dir>; a
change is done when `<check>` is green (see Verification).>

Start with [FEATURE_MAP.md](FEATURE_MAP.md) to find the feature that owns what
you're changing, then read that feature's FEATURE.md.

## Layout

<tree with one line per top-level directory; no per-file lists>

## Dependency rules

| Layer | May import |
| --- | --- |

- Other features only through their public surface (`<surface file>`).
- No cycles between features; when one appears, move the shared piece to `<core>`.
- Promote to `<building blocks>` only on second use.

Enforced by `<structure>`. Use `<graph> <feature>` for a feature's
dependencies, `<graph> <feature> --reverse` for its dependents, and
`<owner> <file>` to find the owning feature and its FEATURE.md.

## Feature anatomy

<the feature template tree: public surface, main files, tests, FEATURE.md;
plus a server-only folder if client and server code share this tree>

- Tests: <placement rule; which suffix or directory belongs to which runner>.
- FEATURE.md: observable behaviour by sub-feature, ending with `## Files`.
- Check FEATURE_MAP.md's shared code tables before writing a helper; core may
  already have it.

## Conventions

Each one names the check that enforces it, or says "review" if only the
review skill checks it.

- Comments in source files: <policy>. Explanations go in FEATURE.md or a test
  name. — `<structure>`
- Suppressions: single line, with an inline reason. — `<structure>`
- Formatting: runs automatically after every edit (<hooks>); otherwise run
  `<fix>`. Never format by hand. — `<format-check>`
- <repo-specific conventions> — <check or "review">
- Nested rules: <each nested AGENTS.md, and what it covers>

## Verification

<see section 3 of this file>

## Running locally

<`<dev-local>` and the local services it starts; how ports, databases and
build directories are isolated per worktree>

Cloud-only: <flows that need real keys, which tests skip locally, and the
command that runs them with keys>.

Environment: run `<env-check>` (or list only variables whose purpose isn't
obvious from their names).

## Adding or changing a feature

1. Find the owning feature in FEATURE_MAP.md and read its FEATURE.md. For a
   new feature, run `<new-feature> <name> "<one sentence: what a user can do>"`,
   which also adds its FEATURE_MAP.md row.
2. Describe the behaviour change in FEATURE.md.
3. Write or adjust the test first, at the right level.
4. Implement inside the feature; export new public pieces from the surface
   file.
5. Iterate with `<check-feature> <feature>`.
6. If the feature's scope changed, update the first line of its FEATURE.md
   (the checker makes you update its FEATURE_MAP.md row to match), and add any
   new name users call it to "Also called".
7. Run `<check>`, plus `<e2e>` if a user flow changed.
8. Self-review the diff with the `<repo>-review` skill, and fix what it finds.

See <worked example path> for a real change, end to end.

## Scripts

<only commands not already in the Verification table: seed/reset, inspect,
env-check, graph, owner, test-coverage. One line each: command — what it does
— when to run it.>

## Tooling notes

<only quirks that have no config line to sit on>
````

## 3. The verification section

This section lets an agent prove a change is correct *and* complete without
asking anyone. Adapt it to the repo's actual commands, and drop rows that
don't exist (e2e, build, dev-local).

**Definition of done**: state it in exactly these words: "A change is not done
until `<check>` is green, `<e2e>` is green if any user flow changed, and every
item in the completeness checklist is ticked."

**Commands**:

| Command | Proves | When |
| --- | --- | --- |
| `<typecheck>` | types hold across the whole project | after each series of edits |
| `<lint>` | framework and correctness rules, with zero warnings | after each series of edits |
| `<structure>` | layers, public surfaces, cycles, anatomy, test placement, docs, suppressions, sync | after adding or moving files |
| `<format-check>` | every file is formatted | before declaring done |
| `<test-baseline>` | all tests pass and none were lost | before declaring done |
| `<check-feature> <feature>` | all of the above for one feature, in seconds | while iterating |
| `<check>` | all of the above for the whole repo | before declaring done |
| `<fix>` | formats and autofixes | when a hook didn't run |
| `<e2e>` | real user flows against keyless local services | after touching any user flow |
| `<check-all>` | `<check>` + e2e | multi-feature changes |
| `<build>` | the production build succeeds | after changing routing, config or deps |

**While iterating**: `<check-feature> <feature>`, `<test runner> <path>`,
`<e2e runner> <path>`.

**Completeness checklist** (correct is not the same as complete). This block is
the canonical copy: the review skill and the bot configs carry synced copies.
List only what `<check>` can't verify.

```markdown
<!-- sync:completeness:start -->
- [ ] New behaviour has a test at the right level (<helper → unit test;
      component → component test; user flow → e2e>), written before the code,
      and the test would fail if the behaviour broke. A new branch with no
      test isn't complete.
- [ ] The owning FEATURE.md describes the new or changed behaviour. If the
      feature's scope changed, its first line (and so its FEATURE_MAP.md row)
      still says what a user can do, and any new name users call it is in
      "Also called".
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
  before changing any code, then rerun the single spec.
- **Lint**: fix the code. A single-line suppression with an inline reason is a
  last resort.
- **A gate seems wrong**: say so in the PR. Don't edit checker rules, lint
  config, the baseline or CI to get to green.

**Cannot be verified locally**: list the cloud-only flows, which tests skip
locally, and the exact command that runs them with real keys. Agents report
these rather than building workarounds.

## 4. FEATURE.md template

One in every feature folder, always named `FEATURE.md` (and in composition
folders, if the repo has them).

```markdown
# <Feature name>

<One sentence: what a user can do with it. The same sentence is the feature's
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
edit their own feature's FEATURE.md, so these docs don't become hotspots.

## 5. FEATURE_MAP.md

`FEATURE_MAP.md` is its own file, next to AGENTS.md, in every repo, however
small. It's the routing table from a request in the user's words ("make
reactions work in threads") to the folder and doc that own it. Agents open it
to answer three questions:

- Which feature owns this behaviour?
- Does a helper for this already exist?
- Where do I start reading?

`<owner> <path>` answers the reverse question (file → feature), so the map
never lists files. AGENTS.md links to it at the top and keeps no feature list
of its own.

### Template

Rename the tables to the layers chosen in Phase 1, and drop tables for layers
the repo doesn't have (the Features table always stays). Within each table,
sort the rows alphabetically. Two agents adding features then insert rows in
different places instead of both appending at the end, so merge conflicts are
rarer.

```markdown
# Feature map

Find the feature that owns a behaviour here, then read its FEATURE.md before
changing anything. The rules are in [AGENTS.md](AGENTS.md). To find the
feature that owns a file, run `<owner> <path>`.

## Features

| Feature | What a user can do | Also called |
| --- | --- | --- |
| [channels](features/channels/FEATURE.md) | Create, browse, join and leave channels. | rooms |
| [reactions](features/reactions/FEATURE.md) | React to a message with an emoji and see who reacted. | emoji, likes |

## Views

| View | Where it appears |
| --- | --- |
| [sidebar](views/sidebar/FEATURE.md) | Left column: workspace switcher, channel list and DMs. |

## Primitives

| Primitive | Use it for |
| --- | --- |
| [avatar](primitives/avatar.tsx) | A user's picture, with a presence dot and initials as the fallback. |

## Shared code

| Module | Reach for it when |
| --- | --- |
| [ids](lib/ids.ts) | You need a room, thread or message id. Never build one by hand. |

## Cross-cutting

- Data model: <where it's defined, in one line>.
- API routes: each `app/api/<name>/route.ts` re-exports one handler from
  `features/<feature>/api/`. Run `<owner>` on a route file to find its feature.
- <Anything else no feature owns, one line each: auth model, realtime model…>

## Not yet migrated

| Legacy path | Moving to |
| --- | --- |
| `components/search/` | `features/search` |
```

### What each column is for

- **What a user can do**: the one sentence from Phase 1 that passed the
  feature test ("can you describe it in one sentence a user would
  understand?"). It's also the first line of the feature's FEATURE.md, word
  for word, and the checker compares the two. So the behaviour is described in
  one place, and the map can't drift from it.
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
  API routes map to features; don't list the routes.
- **Not yet migrated**: only while a migration is unfinished. It tells agents
  where legacy code lives, and where it's going. Delete the section once it's
  empty.

### What never goes in it

- file lists (they belong in FEATURE.md's `## Files`)
- dependencies between features (`<graph>` prints them)
- counts of anything
- behaviour beyond the one sentence (it belongs in FEATURE.md)
- status, owners, roadmap or ticket links (they go stale, and they aren't
  needed to make a change)

### When to write it

| Situation | When |
| --- | --- |
| Before the move (Phase 3.4) | Create it from the plan's feature table, with every feature in "Not yet migrated" (legacy path → target folder). |
| Each migration checkpoint (3.5) | Move the feature's row into the Features table, with the one-sentence summary that's also the first line of its new FEATURE.md. |
| After the move (3.6) | Delete the empty "Not yet migrated" table; fill in "Also called", the building-block and shared code rows, and the cross-cutting notes. |
| A migration left unfinished (very large repos) | The "Not yet migrated" table stays, and later PRs move rows out of it. |
| An existing map | During the drift audit: remove dependency columns, file lists, counts and status; add "Also called"; put it under the checker. |

### Size

Aim for under ~100 lines. When there are too many features for that, group
the Features table under subheadings by product area. In a monorepo, write one
map per package, next to that package's AGENTS.md. The root map then lists only
the packages, each with a one-line summary and a link to the package's map.

### Keeping it true

- The checker's `feature-map` rule (`checks-and-scripts.md`) fails when:
  - FEATURE_MAP.md is missing
  - a feature, composition piece, building block or core module has no row, or
    has more than one
  - a link doesn't resolve
  - a feature's summary differs from the first line of its FEATURE.md
  - rows aren't sorted
  - the "Not yet migrated" table and the checker's legacy-directory config
    disagree
- The scaffolder takes the one-sentence summary as an argument. It writes the
  sentence as the first line of the new FEATURE.md, and inserts the row into
  the map in sorted position. So a freshly scaffolded feature passes `check`.
- Other edits are by hand. Renaming or splitting a feature updates its row in
  the same PR, and the checker fails until it does.
- The "Also called" column isn't checked by a script. The review skill flags a
  PR that introduces a new user-facing name without adding it.

## 6. Nested rules

Rules that matter only for some files go in a nested `AGENTS.md` in the folder
they apply to (the nearest one applies). Examples: e2e locator rules in the
e2e folder, how to use the test backend mock in `tests/`, migration rules next
to the migrations, one package's quirks in that package. This keeps the root
contract short.

- Keep each nested AGENTS.md to the rules for that folder. Don't repeat the
  root contract.
- When a rule applies to a glob that spans folders (`**/*.spec.ts`), put it in
  the nested AGENTS.md of the folder most of those files live in, or in a
  short root section if they're scattered.
- If the team also uses a tool with its own glob-scoped rules (Cursor's
  `.cursor/rules/*.mdc`, Copilot's `.github/instructions/*.instructions.md`),
  give it a copy between `sync` markers, which the checker compares.

## 7. Worked example doc

Write this as `docs/EXAMPLE_CHANGE.md`, or as a short AGENTS.md section.
Agents pattern-match on it, and reviewers can point to it.

- **Preferred**: the first feature-sized change made after the restructure, so
  every path in it is real.
- **Otherwise**: a representative change from history (new behaviour inside
  one feature, with tests and docs). Rewrite its paths through the migration's
  move map, and say that you rewrote them.
- **Never invent one.** If neither exists yet, list it as a follow-up.

```markdown
# Worked example: <change>

Commit(s): <sha> — <one line>. Chosen because <it touched one feature end to end>.

## Order of work
1. FEATURE.md: described the new behaviour (`<path>`)
2. Test, written first: `<path>`: <what it asserts>
3. Model or logic: `<path>`: <what changed>
4. UI or handler: `<path>`
5. Public surface: exported `<name>` from `<surface file>`
6. E2E: `<path>`

## Commands
`<check-feature> <feature>` (caught: <…>), `<check>`, `<e2e> <path>`

## What review caught that the checks didn't
<…, or "nothing">
```
