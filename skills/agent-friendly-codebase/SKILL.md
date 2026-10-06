---
name: agent-friendly-codebase
description: >-
  Audit a codebase in any language or framework and restructure it so many AI
  agents can build, test and verify changes in parallel without colliding.
  Chooses a layout from what the code and its git history already show (units
  with one owner folder and a public surface, one-way dependencies enforced by
  a checker), then adds a short AGENTS.md contract with a definition of done,
  a feature map that routes requests to their owning folder, one check command with scoped and fix variants, CI that enforces it, a test
  baseline, scaffolding, keyless and parallel-safe local runs, and a
  repo-specific code-review skill with AI reviewer config. Use when asked to
  make a repo agent-friendly or agent-ready, compartmentalise features, set up
  for parallel agents, write or slim down AGENTS.md, or audit agent readiness.
  Always audits and reports first and changes nothing until the user approves
  the plan.
disable-model-invocation: true
---

# Agent-friendly codebase

The target is a codebase where an agent can:

1. **Find** the one folder that owns a behaviour.
2. **Change** it without editing files another agent is editing, and without
   colliding at runtime (ports, databases, build directories).
3. **Learn** the rules from a short contract plus docs that sit next to the
   code.
4. **Prove** the change is correct and complete with one command, and iterate
   with a faster scoped one.
5. **Get reviewed** on what the checks can't catch, by a reviewer that knows
   this repo.

Every decision in this skill serves one of those five. When something comes up
that the skill doesn't cover, choose whatever serves them best for *this* repo
and say why in the report. The folder names in the examples are illustrations,
not the goal.

Two ground rules:

- **Nothing changes before the user approves the report.** A restructure is
  large, and the user owns naming, scope and what to skip.
- **Fit the intervention to the repo.** Every layer, script and doc has an
  upkeep cost. A 25-file CLI might need only units + core, one `check`, a short
  AGENTS.md, CI and a review skill. "Keep the layout and add the contract" is
  always a candidate.

## Modes

| The user wants                                          | Do                                                                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| An audit ("how agent-ready is this?")                   | Phases 0–2, then stop                                                                                         |
| To make the repo agent-friendly                         | All phases                                                                                                    |
| A repo that already has a contract (AGENTS.md, checker) | Phase 0 with the drift audit → Phase 2 (gaps only) → the approved 3.x steps → the matching Phase 4 checks    |
| One app inside a larger repo                            | Scope everything to that path, match the parent's configs, and put nested files (AGENTS.md, reviewer config, CI filter) in the app |

## Bundled files (read or run each one when you reach its step)

| File                               | Use at                                                                    |
| ---------------------------------- | ------------------------------------------------------------------------- |
| `scripts/cochange.py`              | Phase 0 (hotspots, co-change, locality) and Phase 1 (score candidates)    |
| `references/choosing-structure.md` | Phase 1: archetypes, units, layers, comparing candidates, worked examples |
| `references/toolchains.md`         | Phase 0 (test counts), 3.0 (commands and invocation), 3.4, 3.9 (skip and suppression syntax) |
| `references/checks-and-scripts.md` | 3.1, 3.5–3.7: checker rules, baseline, scaffold, scoped check, scripts    |
| `references/contract.md`           | 3.3: AGENTS.md, feature map, unit docs, scoped rules, verification, worked example |
| `references/ci-and-review.md`      | 3.8–3.9: CI, gate protection, review skill, AI reviewer config            |
| `assets/review-skill-template.md`  | 3.9: the review skill you generate for the repo                           |

`cochange.py` needs Python 3 and git, and nothing else. Run it from the target
repo as `python3 <this skill's folder>/scripts/cochange.py .`. It writes
nothing. On a shallow clone it warns you; fetch the full history first.

## Phase 0: Audit (read-only)

Phase 0 changes nothing in the repo. Anything that needs to write files (such as
a scaffold test) runs in a throwaway `git worktree`. Write down what you find,
with evidence (paths and command output):

- **Stack**: languages, frameworks, package or workspace manager, runtime
  versions, task runner, test runners, formatter, linter, typechecker, build.
- **CI**: which workflows exist, whether they cover this code path, whether any
  check is a required status (rulesets or branch protection, via `gh api` when
  you have access), and whether CODEOWNERS exists.
- **Agent tooling in use**: `AGENTS.md`, `CLAUDE.md`, `.cursor/` (rules,
  `BUGBOT.md`), `.github/copilot-instructions.md`, `.github/instructions/`,
  `.coderabbit.yaml`, `.claude/`, `.agents/skills/`. This decides where docs,
  scoped rules, the review skill and reviewer config will go. If there's no
  sign of any tool, ask which ones the team uses.
- **Shape**: the current layout and where logic actually lives;
  framework-mandated directories; entry points (routes, handlers, commands,
  `main`); existing module or package boundaries and anything already
  enforcing them; generated, vendored and migration code.
- **History**: `cochange.py . [--root <app>] [--depth N]` reports three things:
  - hotspot files
  - which areas change together
  - current locality: the share of recent commits that touched exactly one
    area

  An "area" is a directory at the depth where units would sit (often 1, or 2
  under `src/`). Files that always change together belong in one unit, and a
  file that changes alongside everything is a hotspot.
- **Candidate units**: user-facing capabilities, found from routes, screens,
  commands and endpoints, cross-checked against the co-change clusters. Note
  the other names users and the team give each one (UI copy, issue titles,
  docs), for the feature map's "Also called" column.
- **Tests**: files and tests per runner, using machine-readable counts (see
  `toolchains.md`). These become the baseline. Also note skipped tests, flaky
  markers, and whether tests run against a real local backend or mocks (and
  which one the project prefers).
- **Shared code and hotspots**: helpers, types and config that several units
  need; any `utils` junk drawer; files that every change touches (route tables,
  DI containers, central types, i18n catalogues, a single changelog, global
  styles). Each one is a merge-conflict risk for parallel agents.
- **Comments**: a rough count, and what they explain (behaviour, tooling
  quirks, invariants, stale TODOs).
- **Running without secrets**: whether the code and its tests can run locally
  with no keys (local backend, emulator, docker compose, mocks), and what needs
  real credentials. For a library or CLI, this means whether the tests and
  examples run without keys.
- **Running in parallel**: can two copies of the test suite (and the app, if it
  runs as a process) run at once in two worktrees? Look for fixed ports, a
  shared local database or emulator state, shared build or cache directories,
  and global temp paths.
- **Open work**: open PRs and active branches (`gh pr list`,
  `git branch -r --sort=-committerdate`). A restructure will conflict with all
  of them.
- **Manual toil**: what an agent currently does by hand, such as setting up
  env, seeding data, inspecting backend state, or working out which file owns a
  behaviour. These are the candidates for scripts.

**If a contract already exists**, also check for drift. These are the failure
modes that show up after a repo has been made agent-friendly once:

- `check` exists, but CI doesn't run it or it isn't a required status. When
  present, this is the top finding: checks only run if an agent remembers to
  run them.
- AGENTS.md is long and mirrors the code: inventories, dependency columns,
  lists of shared modules, counts in prose. Compare every count with reality;
  they're usually already wrong.
- Unit docs' file lists match their folders by luck rather than because a
  check enforces it.
- The feature map is missing, lists files, dependencies or status, or has rows
  that don't match the units and their docs.
- Rules that only matter for some files (test locators, migrations, one
  package) sit in the always-loaded AGENTS.md instead of a scoped rule file.
- Scaffold output contradicts the rules. In a throwaway worktree, scaffold a
  unit, run the full `check`, and read the generated code against the
  conventions.
- There's no fast scoped check or `fix` command, or checker messages say
  what's wrong but not what to do.
- Large files (over ~300 lines) in units, and which of them are growing.
- The worked example is missing, or it points at paths that no longer exist.
- Reviewer config is missing, or is long and restates what `check` already
  enforces.
- Suppressions in the code have no reason attached, or don't match the
  documented exceptions.
- Gate files (checker, CI, lint config, baseline, review skill) can be changed
  without a code-owner review.

## Phase 1: Decide the structure

Read `references/choosing-structure.md`, then:

1. **Classify** the repo: UI app, service/API, CLI, library/SDK, monorepo, data
   pipeline, or a mix. For a mix, classify each part.
2. **Choose units** and name them in the product's vocabulary, following the
   language's naming convention. Test each candidate: could one agent own it
   for a week without editing another unit's folder? Can you describe it in
   one sentence a user would understand? Write that sentence down: it becomes
   the unit's feature-map row and the first line of its doc. Assign every
   source file to a unit or layer, or list it as ambiguous for the user to
   decide.
3. **Choose layers** from the ladder entry → composition → units → building
   blocks → core. Drop any layer the repo doesn't need, and name the rest in
   the ecosystem's idiom.
4. **Keep the framework's grain.** Framework-mandated directories stay. Where
   the language or framework already enforces boundaries (packages, crates,
   Django apps, modules, workspace packages), use those rather than inventing a
   parallel set.
5. **Compare candidates on evidence.** Always include "keep the layout and add
   the contract", plus one or two restructures. For each restructure, write a
   map file from the paths in history to its units, and run
   `cochange.py . --map <file>`. It scores today's layout and the candidate on
   the same basis. Recommend a restructure only when its simulated locality
   beats today's by a clear margin (as a rule of thumb, 15 points or more) and
   the disruption (files moved, open branches that will conflict, friction with
   the framework) is acceptable to the user. Otherwise, recommend keeping the
   layout, adding the contract, and moving only the worst offenders.
6. **Pick one test-placement convention** that fits the language.
7. **Pick the enforcement.** Use an established ecosystem tool for import rules
   where a good one exists, plus a small repo script for the rules no generic
   tool knows about (anatomy, docs, suppressions, sync).
8. **Pick a migration strategy.** Either move everything in checkpoints
   (big-bang), or go incremental: contract, check and CI first, then one unit at
   a time, with the checker ignoring legacy directories until each one is
   emptied. Recommend incremental for large repos, busy repos, or repos with
   many open branches.

## Phase 2: Report and get approval

Write the report below, then stop and ask. Use the question tool if you have one
(AskUserQuestion, AskQuestion); otherwise ask in conversation. Don't start
Phase 3 until each numbered item has an explicit yes, no or modify. If the
request has a real problem (the repo is too small to benefit, or the framework
fights the layout), say so in one or two sentences, then proceed under stated
assumptions if the user reaffirms.

```markdown
# Agent-readiness report: <repo>

## Current state
- <stack, tooling, CI coverage, required checks, CODEOWNERS, agent tools in use>
- Tests: <runner>: <files> files / <tests> tests (proposed baseline)
- Locality today: <x>% of the last <N> commits touched one area
- Hotspots: <files>, and why each one is a collision risk
- Comments: <count>; mostly <what they explain>
- Runs without secrets: <yes / no / how>; runs in parallel: <yes / blockers>
- Open branches/PRs the restructure would conflict with: <n>
- Drift found: <only if a contract already exists>

## Options
| Option | Locality (same basis) | Files moved | Conflicts with open work | Notes |
| ------ | --------------------- | ----------- | ------------------------ | ----- |
| Keep layout + contract | <today's %> | 0 | none | |
| <restructure A>        | <%>         | <n> | <n branches> | |

## Recommended shape
<One paragraph: the archetype, why this layout fits, which framework
conventions it keeps, and the migration strategy.>

<tree, using the layer names chosen for this repo>

| Layer | May import |
| ----- | ---------- |

## Feature map (draft)
| Unit | What a user can do (one sentence) | Also called | Current files | Depends on |
| ---- | --------------------------------- | ----------- | ------------- | ---------- |
<plus rows for composition, building blocks and core modules; then any ambiguous files.
After approval, this becomes FEATURE_MAP.md without the last two columns.>

## Proposed changes (approve each)
1. Structure, public surfaces, and a boundary checker with graph/owner lookups
2. Test placement: <convention>
3. Comments policy for source files: <none / public API docs only / unchanged>   (ask!)
4. AGENTS.md contract, FEATURE_MAP.md, unit docs, scoped rule files, worked example
5. Commands: check, check-unit, fix, check-all (named for <task runner>)
6. Formatter enforced: <tool>
7. Linter with zero warnings: <tool>; <n> existing findings and the triage plan
8. Suppressions carry an inline reason, enforced by the checker
9. Test baseline that may only go up
10. Scaffolder: <kinds>
11. Keyless, parallel-safe local runs: <how>
12. CI running check as a required status, plus CODEOWNERS on gate files   (recommended)
13. Review skill for this repo, plus config for: <AI reviewers in use>
14. File-size warning at ~300 lines
15. Coverage report on demand, not a gate                                  (optional)
16. Other scripts from the audit: <seed/reset, inspect, env-check…>

## Decisions I need from you
- Doc names: FEATURE.md per unit (greppable, unambiguous) or README.md (rendered
  by GitHub in the folder view)? And FEATURE_MAP.md for the map, or
  MODULE_MAP.md if "feature" reads oddly for this repo?
- Comments: remove, keep public API docs only, or leave as they are?
- Migration: big-bang in checkpoints, or incremental?
- Which AI reviewers you use (or want), and where your agents load skills from.
- Anything above to skip or change?
```

## Phase 3: Implement (after approval)

Work in checkpoints and run the relevant gates after each one. Don't move
everything and test at the end.

### 3.0 Gates first

Add the commands before moving any files, so every later step has a gate. Name
and invoke them the way the repo's task runner expects; `toolchains.md` has an
invocation table per runner. The roles:

| Role            | Does                                                                     |
| --------------- | ------------------------------------------------------------------------ |
| `typecheck`     | types or compilation across the whole project                            |
| `lint`          | the linter, with warnings failing                                        |
| `structure`     | the boundary checker (3.1)                                               |
| `format-check`  | the formatter in check mode                                              |
| `test-baseline` | unit and integration tests, plus the baseline comparison                 |
| `e2e`           | end-to-end flows against a local backend, with no keys (if the repo has user flows) |
| `check`         | all of the above except e2e, cheapest first, failing fast                |
| `check-unit`    | the same, scoped to one unit or path; takes seconds; for iterating       |
| `check-all`     | `check` + `e2e`                                                          |
| `fix`           | formatter write + linter autofix                                         |
| `dev-local`     | runs the app with no secrets (if it runs as a process)                   |
| `new-<kind>`    | the scaffolder                                                           |
| `graph`, `owner` | modes of the boundary checker (3.1)                                     |

Write the *rules* half of AGENTS.md now (layout, dependency rules, anatomy,
conventions, verification). Write anything inventory-like after the move, so
nothing goes stale mid-migration.

### 3.1 Boundary checker

Build it before migrating, because it's the map you migrate against. Include
the `graph` (unit dependencies, forward and reverse) and `owner` (file → unit
and doc) modes: the docs, the review skill and agents all rely on them in place
of hand-written tables. The rules and the output format are in
`checks-and-scripts.md`. While migrating, the checker ignores legacy
directories; once a legacy directory is empty, add it to the "must not
reappear" list. Negative-test every rule: create a violation, confirm it fails
with a message that says what to do, then remove it.

### 3.2 Migrate in checkpoints

Order: core → building blocks → units → composition → thin entry. After each
step, run the typecheck or build, `structure` and the affected tests. After the
last step, run `check-all` and a build.

- Move files with `git mv` so history survives. If the user wants commits, make
  one per checkpoint, so the change can be reviewed and bisected.
- Fix cycles by moving the shared piece down to core, never by widening a rule.
- Never add a type escape or suppression to make a move compile
  (`toolchains.md` lists the syntax per language). Surface the type problem
  instead.
- Behaviour must not change during a restructure. If a test fails after a move,
  the move is wrong, not the behaviour. If you find a real bug, list it as a
  follow-up rather than fixing it mid-move.
- Mechanical moves and comment stripping can go to cheaper subagents with exact
  file lists. Verify their output mechanically, with a diff that ignores
  comments, imports and whitespace. Known failure modes: blank lines left where
  comments were (inside type definitions and empty `catch` blocks), behaviour
  "fixed" to satisfy a new test, and imports rewritten as deep paths.
- If a comments policy applies, it covers source files only. Config files keep
  their comments next to the lines they explain. Explanations removed from
  source go to: user-observable behaviour → the unit doc; invariants → a test
  whose name states the invariant; tooling reasons → the config file, or
  AGENTS.md "Tooling notes" if there's no config line to put them on.

### 3.3 Contract docs

Follow `contract.md`. You're writing:

- a short AGENTS.md (it's loaded on every task, so aim for under ~150 lines)
- one unit doc per unit
- the feature map (`FEATURE_MAP.md`): the routing table from a request in the
  user's words to the unit that owns it, with what users call each unit and
  what each shared module is for. Build it from the approved draft in the
  report. AGENTS.md links to it rather than importing it, and the checker keeps
  it complete and in step with the unit docs (`contract.md` §5)
- scoped rule files for rules that only apply to some paths
- a worked example
- pointers for tools that don't read AGENTS.md (for example, a `CLAUDE.md`
  containing `@AGENTS.md`)

The governing rule: never write in prose what a command can print or a checker
can verify. When moving existing prose, move it verbatim, then grep the
original lines against the new files to prove nothing was lost.

### 3.4 Formatter, linter and suppressions

- Use a formatter config that matches any parent config. Ignore build output,
  lockfiles and generated code. Reformat everything once, in its own commit, so
  the reformat doesn't bury real changes in review.
- Use the linter with the framework's preset, and make warnings fail. Triage
  every existing finding:
  - fix it properly where you can
  - turn off rules that don't fit the codebase, with the reason as a comment in
    the lint config
  - for deliberate patterns, add a single-line suppression on exactly that line,
    with the reason inline (for example `// eslint-disable-next-line rule --
    reason`, `# noqa: E501  # reason`, `#[allow(x, reason = "…")]`)
- The checker's `suppressions` rule fails on any suppression without a reason.
  Keeping reasons inline (rather than in a central exception table) means
  parallel agents never collide on one file. If a legacy codebase has too many
  reasonless suppressions to triage now, grandfather them in a generated
  allowlist that may only shrink.

### 3.5 Test baseline

Keep the counts in a committed file that may only go up, and never put counts
in prose. Locally, the baseline rises automatically. In CI, a count higher than
the committed one fails as "stale baseline: commit it". The spec is in
`checks-and-scripts.md`.

### 3.6 Scaffolder

Its output must pass every check and follow every convention: agents copy
scaffolded code more than anything else. Spec in `checks-and-scripts.md`.

### 3.7 Local runs and other scripts

- `dev-local` (when the code runs as a process) starts a local backend with no
  secrets. Verify it with `curl` or a smoke test.
- Make local runs **parallel-safe**:
  - take ports from env, with a free-port fallback
  - give each worktree its own local database or emulator state, and its own
    temp and build directories (frameworks that lock a build directory need a
    separate one per server)
  - put these directories in the ignore files

  Two agents in two worktrees must be able to run `check-all` at the same time.
- Build the scripts the user approved from the audit (seed/reset, inspect,
  env-check). The rules for every script are in `checks-and-scripts.md`.

### 3.8 CI and gate protection

Follow `ci-and-review.md`. CI runs the same `check` command agents run (never a
separate list of steps), plus e2e, as required statuses; watch for the
path-filter trap described there. Put the gate files (listed in that file's
"Protecting the gates" section) under CODEOWNERS with required code-owner
review, so a change can't loosen its own gate. Treat
this step as core: without CI enforcing it, the contract is only a suggestion.

### 3.9 Review skill and AI reviewer config

Generate a review skill for this repo from `assets/review-skill-template.md`.
Fill it with the repo's commands, docs, scoped rules, hotspots, and the
specific hazards the audit found. Put it wherever the team's agents load
skills. When you're done, grep the result for `{{`: nothing should remain.
Then add thin config for the AI reviewers the team uses, as described in
`ci-and-review.md`. Reviewers should spend their budget on what `check` can't
see, and any finding that keeps recurring should become a check.

### 3.10 Optional: coverage on demand

Add `test-coverage`, but not as a gate. Agents run it on the unit they touched
and read the unexecuted lines. A global threshold is easy to game and slows
every run.

## Phase 4: Verify and report

Run these and report the actual numbers:

1. `check`, then `e2e` and a production build where they exist.
2. A negative test of every checker rule, and of the baseline: lower the count
   and expect a failure; raise it with `CI=true` and expect a "stale" failure.
3. Scaffold each kind → full `check` (the scaffolder added the feature-map row,
   so it should pass) → delete the unit and the row.
4. `check-unit` on one unit, and `fix` on a deliberately misformatted file.
5. Two `check-all` runs at once, in two worktrees.
6. A `dev-local` smoke test, if the code runs as a process.
7. Every new script, with bad arguments (usage is shown) and good arguments.
8. CI: lint the workflow (`actionlint` if available), run it on a branch if you
   can, and confirm the required-status and CODEOWNERS setup with the user.
9. A review skill dry run, against a small seeded diff with two problems: one
   the checks can't catch (for example, a behaviour change with no unit doc
   update) and one they can. Confirm the skill reports the first and leaves
   the second to `check`.
10. AGENTS.md covers: the definition of done, the commands and when to run
    them, scoped runs, the completeness checklist, failure guidance, what can't
    be verified locally, and the worked example. It contains no counts and no
    inventories that a command could print. FEATURE_MAP.md has a row for every
    unit, block and core module, and each row tells an agent something the
    tree can't (what a user can do, what it's also called, when to reach for
    it).
11. `cochange.py . --map <move map>` (the paths in history mapped to the final
    units), so the report has the predicted locality next to today's number.
12. `git status`: no build artefacts staged, and the baseline is committed.

Then report:

- what moved where
- which rules are now enforced, and by which check
- the suppressions triaged
- tests before vs after (the count must not drop)
- locality before vs predicted after
- the scripts added and the reviewer setup
- anything skipped, and why
- follow-ups you recommend but didn't do

## Principles

- The code and its checks are the contract. Prose is the index to them. A
  list in prose is fine only when each item adds something the tree can't show
  (a one-line purpose) and a check keeps the list complete. Counts never are.
- Anything a reviewer flags twice becomes a check.
- One convention per concern beats several reasonable ones.
- Restructure toward locality, not toward a particular folder tree.
- Script output is read by an agent with no context. Say what failed, where,
  why, and what to do next.
- Delegate mechanical work, and verify it mechanically.
