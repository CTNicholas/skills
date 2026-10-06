---
name: agent-friendly-codebase
description: >-
  Audit a codebase in any language or framework and restructure it so many AI
  agents can build, test and verify changes in parallel without colliding.
  Puts every feature in its own folder (boundaries chosen from the code and its
  git history), writes a test suite first and keeps it green through the move,
  and adds an AGENTS.md contract, a separate FEATURE_MAP.md, a FEATURE.md per
  feature, one check command with scoped and fix variants, formatting after
  every agent edit, keyless local runs, CI, and a repo-specific code-review
  skill with AI reviewer config. Fire and forget: audits, shows one plan, asks
  one yes or no (plus which AI reviewer, if none is set up), then does the
  rest. Use when asked to make a repo agent-friendly or agent-ready,
  compartmentalise features, set up for parallel agents, or audit agent
  readiness.
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
that the skill doesn't cover, choose whatever serves them best for *this* repo,
and record the call in the final report. The folder names in the examples are
illustrations, not the goal.

## How this skill runs

- **One question, then fire and forget.** Audit, decide everything using the
  defaults below, show a short plan, and ask once: go ahead, yes or no. If the
  repo has no AI reviewer configured, the same prompt also asks which one to
  set up. After a yes, ask nothing else. When something unexpected comes up,
  make the call that best serves the five goals, keep going, and list the call
  in the final report.
- **Nothing changes before the yes.** Phases 0 to 2 are read-only.
- **Never trim the core.** Every repo gets feature folders, `AGENTS.md`,
  `FEATURE_MAP.md`, a `FEATURE.md` per feature, a test suite, one `check`
  command, formatting after every edit, CI and a review skill. Scale only the
  extras (composition and building-block layers, scaffold kinds, extra
  scripts) to what the repo needs.

## Defaults

These replace questions. Where the repo already has an established choice,
keep the repo's.

| Topic | Default |
| --- | --- |
| Features | One folder per feature, in the ecosystem's idiom: `features/<name>/`, a Go package, a Django app, a crate, a workspace package. Existing modules that are technical layers (`handlers/`, `services/`, `components/`) or hold several features are split. Framework-mandated directories stay, as a thin entry layer. |
| Docs | `AGENTS.md` (the contract), `FEATURE_MAP.md` (a separate file next to it) and `FEATURE.md` in every feature folder. No `CLAUDE.md`: agents read `AGENTS.md`. If a `CLAUDE.md` exists, move anything still true into `AGENTS.md` and delete it. |
| Tests | Per role (unit, component, e2e): the runner the repo already has. For an empty role: Vitest for JS/TS unit tests, Testing Library on the repo's unit runner for components, Playwright for e2e in web apps, and the ecosystem's standard runner elsewhere (`toolchains.md`). Tests are written before anything moves. |
| Formatting | The formatter already in the repo; if there's none, Prettier for JS/TS and the ecosystem's standard formatter elsewhere. It runs automatically on every file an agent edits, through post-edit hooks, and `format-check` runs in `check` and CI. |
| Linting | The repo's linter, or the framework's preset if there's none, with warnings failing. |
| Comments | None in source files. Explanations move to `FEATURE.md`, `AGENTS.md` or test names. Keep doc comments on public APIs where the language's tooling uses them (Go exported identifiers, Rust `///`, a published library's docstrings). Magic comments and suppression reasons are always allowed. |
| Local runs | Keyless wherever the services allow it: each external service the app uses is wired to its local dev server, emulator, container or mock. Flows with no local option are listed as cloud-only. |
| Branch | A new branch, `agent-friendly`, from the current HEAD; in a separate worktree if the working tree has uncommitted changes, so they're never touched. One commit per step. Nothing is pushed. |
| Migration | Feature by feature in this session. For very large repos (roughly 500+ source files), do the gates, tests, contract and the first features now, and leave the rest in `FEATURE_MAP.md`'s "Not yet migrated" table. |
| CI | The CI system already in use; GitHub Actions if there's none and the repo is on GitHub. |
| AI reviewer | Whatever is already configured. If nothing is, it's the one question in Phase 2. |
| Agent tools | Configure hooks and skills for the agent tools the repo shows signs of (`.claude/`, `.cursor/`, `.codex/`, `.agents/`, `.github/copilot-instructions.md`). With no signs, configure Claude Code and Cursor. |
| Review skill location | Wherever the repo already keeps skills; otherwise `.claude/skills/<repo>-review/`, which several agents read (`ci-and-review.md` §5). |
| Repo settings | Never change rulesets, branch protection or app installs. The final report lists them as follow-ups with exact commands (making CI required, CODEOWNERS if there's none, installing the reviewer). |

## Modes

| The user wants | Do |
| --- | --- |
| An audit ("how agent-ready is this?") | Phases 0 and 1, then present the plan as findings and stop. No question. |
| To make the repo agent-friendly | All phases |
| A repo that already has a contract (AGENTS.md, checker) | Phase 0 with the drift audit; the plan covers only the gaps |
| One app inside a larger repo | Scope everything to that path, match the parent's configs, and put nested files (AGENTS.md, FEATURE_MAP.md, reviewer config, CI filter) in the app |

## Bundled files (read or run each one when you reach its step)

| File | Use at |
| --- | --- |
| `scripts/cochange.py` | Phase 0 (hotspots, co-change, locality), Phase 1 (drawing boundaries), Phase 4 |
| `references/choosing-structure.md` | Phase 1: archetypes, features, layers, boundaries, test placement, worked examples |
| `references/toolchains.md` | Phase 0, 3.0 (commands, default tools, format-on-edit hooks), 3.1 (keyless backends), 3.2 (test runners), 3.3 and 3.5 (suppression syntax) |
| `references/checks-and-scripts.md` | 3.0 (format script), 3.2 (baseline), 3.4 (checker), 3.7 (scaffolder), 3.8 (scripts) |
| `references/contract.md` | 3.0 (AGENTS.md rules), 3.4 (FEATURE_MAP.md), 3.5 (FEATURE.md), 3.6 (the rest) |
| `references/ci-and-review.md` | 3.9, 3.10: CI, gate protection, review skill, AI reviewer config |
| `assets/review-skill-template.md` | 3.10: the review skill you generate for the repo |

`cochange.py` needs Python 3 and git, and nothing else. Run it from the target
repo as `python3 <this skill's folder>/scripts/cochange.py .`. It writes
nothing. On a shallow clone it warns you; fetch the full history first.

## Phase 0: Audit (read-only)

Phase 0 changes nothing in the repo. Anything that needs to write files (such as
a scaffold test) runs in a throwaway `git worktree`. Write down what you find,
with evidence (paths and command output):

- **Git state**: current branch, whether the working tree has uncommitted
  changes, and the default branch.
- **Stack**: languages, frameworks, package or workspace manager, runtime
  versions, task runner, test runners, formatter, linter, typechecker, build.
  Note every empty role: no unit runner, no component tests, no e2e, no
  formatter, no linter.
- **CI**: which workflows exist, whether they cover this code path, whether any
  check is a required status (rulesets or branch protection, via `gh api` when
  you have access), and whether CODEOWNERS exists.
- **Agent tooling**: `AGENTS.md`, `CLAUDE.md`, `.claude/` (settings, hooks,
  skills), `.cursor/` (rules, hooks, `BUGBOT.md`), `.codex/`, `.agents/skills/`,
  `.github/copilot-instructions.md`, `.github/instructions/`, `.coderabbit.yaml`.
  Note whether agent edits are already formatted automatically (post-edit
  hooks), and which AI reviewer, if any, is configured.
- **Shape**: the current layout and where logic actually lives;
  framework-mandated directories; entry points (routes, handlers, commands,
  `main`); existing module or package boundaries and anything already
  enforcing them; generated, vendored and migration code.
- **History**: `cochange.py . [--root <app>] [--depth N]` reports three things:
  - hotspot files
  - which areas change together
  - current locality: the share of recent commits that touched exactly one
    area

  An "area" is a directory at the depth where features would sit (often 1, or
  2 under `src/`). Files that always change together belong in one feature, and
  a file that changes alongside everything is a hotspot.
- **Features**: user-facing capabilities, found from routes, screens, commands
  and endpoints, cross-checked against the co-change clusters. Note the other
  names users and the team give each one (UI copy, issue titles, docs), for the
  feature map's "Also called" column.
- **Tests**: files and tests per runner, using machine-readable counts (see
  `toolchains.md`). Note skipped tests, flaky markers, and whether tests run
  against a real local backend or mocks. List each feature's main user flows
  and which of them no test covers today.
- **External services**: every backend, API and SaaS the app calls (database,
  auth, realtime, payments, email, storage, AI), and whether each one has a
  local dev server, emulator, container or mock that needs no keys
  (`toolchains.md`, "Keyless local backends"). Note whether the local runtime
  it needs (Docker, a CLI) is available on this machine.
- **Running in parallel**: can two copies of the test suite (and the app, if it
  runs as a process) run at once in two worktrees? Look for fixed ports, a
  shared local database or emulator state, shared build or cache directories,
  and global temp paths.
- **Shared code and hotspots**: helpers, types and config that several features
  need; any `utils` junk drawer; files that every change touches (route tables,
  DI containers, central types, i18n catalogues, a single changelog, global
  styles). Each one is a merge-conflict risk for parallel agents.
- **Comments**: a rough count, and what they explain (behaviour, tooling
  quirks, invariants, stale TODOs).
- **Lint**: run the linter (or the default preset in a throwaway worktree) and
  count the findings.
- **Open work**: open PRs and active branches (`gh pr list`,
  `git branch -r --sort=-committerdate`). The move will conflict with them.
- **Manual toil**: what an agent currently does by hand, such as setting up
  env, seeding data, inspecting backend state, or working out which file owns a
  behaviour. These are the candidates for extra scripts.

**If a contract already exists**, also check for drift. These are the failure
modes that show up after a repo has been made agent-friendly once:

- `check` exists, but CI doesn't run it or it isn't a required status. When
  present, this is the top finding: checks only run if an agent remembers to
  run them.
- AGENTS.md is long and mirrors the code: inventories, dependency columns,
  lists of shared modules, counts in prose. Compare every count with reality;
  they're usually already wrong.
- A `CLAUDE.md` duplicates or contradicts AGENTS.md.
- `FEATURE_MAP.md` is missing, lists files, dependencies or status, or has rows
  that don't match the features and their docs.
- `FEATURE.md` file lists match their folders by luck rather than because a
  check enforces it.
- Rules that only matter for some files (test locators, migrations, one
  package) sit in the root AGENTS.md instead of a nested one.
- Agent edits aren't formatted automatically.
- Scaffold output contradicts the rules. In a throwaway worktree, scaffold a
  feature, run the full `check`, and read the generated code against the
  conventions.
- There's no fast scoped check or `fix` command, or checker messages say
  what's wrong but not what to do.
- Large files (over ~300 lines) in features, and which of them are growing.
- The worked example is missing, or it points at paths that no longer exist.
- Reviewer config is missing, or is long and restates what `check` already
  enforces.
- Suppressions in the code have no reason attached.

## Phase 1: Decide (read-only)

Read `references/choosing-structure.md`, then decide everything yourself:

1. **Classify** the repo: UI app, service/API, CLI, library/SDK, monorepo, data
   pipeline, or a mix. For a mix, classify each part.
2. **Choose the features** and name them in the product's vocabulary, following
   the language's naming convention. Test each one: could one agent own it for
   a week without editing another feature's folder? Can you describe it in one
   sentence a user would understand? Write that sentence down: it becomes the
   feature's row in `FEATURE_MAP.md` and the first line of its `FEATURE.md`.
   Assign every source file to a feature or a layer. Where a file is
   ambiguous, pick the most likely owner and note it.
3. **Choose layers** from the ladder entry → composition → features → building
   blocks → core. Drop any layer the repo doesn't need, and name the rest in
   the ecosystem's idiom.
4. **Keep the framework's grain.** Framework-mandated directories stay as the
   entry layer. Where the language or framework has a module concept
   (packages, crates, Django apps, workspace packages), feature folders take
   that form, one per feature.
5. **Draw the boundaries on evidence.** Every feature gets its own folder; the
   evidence decides where the lines go. Write one or two candidate maps (paths
   in history → features) and score them with `cochange.py . --map <file>`.
   Pick the one with the best locality, then fix the boundaries the recurring
   multi-feature combinations point at (`choosing-structure.md` §6).
6. **Plan the safety net.** For each feature, list the main flows to pin with
   e2e, API or CLI-level tests. For every module headed for core or building
   blocks, and any pure logic the move touches, list the unit tests. These are
   written before anything moves.
7. **Pick the enforcement.** Use an established ecosystem tool for import rules
   where a good one exists, plus a small repo script for the rules no generic
   tool knows about (anatomy, docs, suppressions, sync).
8. **Size the migration** using the Defaults table.

## Phase 2: Plan and the one question

Write the plan below. Keep it short (well under a page); it's for a yes or no,
not a design review. It must name every disruptive action, so the yes covers
them.

```markdown
# Agent-friendly plan: <repo>

## Today
- <stack>; tests: <runners and counts, or "none">; formatter: <tool or "none">;
  CI: <system or "none">; AI reviewer: <tool or "none">
- Locality: <x>% of the last <N> commits touched one area
- Hotspots: <files>
- Keyless: <services with a local option>; cloud-only: <services without one>

## Features
| Feature | What a user can do | Also called | Moves from |
| --- | --- | --- | --- |

## New layout
<tree, using the layer names chosen for this repo>

## What I'll do
1. Work on a new branch, `agent-friendly`<, in a separate worktree because you
   have uncommitted changes>. One commit per step; nothing is pushed.
2. Gates: `check`, `check-feature`, `fix` and the rest. <Formatter> runs after
   every agent edit<; the whole repo is reformatted once, in its own commit>.
   <Linter> with zero warnings (<n> findings to fix).
3. Keyless local runs against <local services>.
4. Tests first: <tools>; e2e for <n> flows and unit tests for <what>, all green
   before anything moves.
5. A boundary checker, then the move, feature by feature, keeping every test
   green. Each feature gets its tests, a FEATURE.md and a FEATURE_MAP.md row as
   it moves.
6. <n> comments removed from source files (explanations move to FEATURE.md or
   test names)<; CLAUDE.md folded into AGENTS.md and deleted>.
7. AGENTS.md, a scaffolder, CI and the review skill<, plus <reviewer> config>.

Predicted locality after the move: <y>%. <Anything unusual: an ambiguous file,
a big hotspot, open branches that will conflict.>
```

Then ask once, with the question tool if you have one (AskUserQuestion,
AskQuestion), or in a single message if you don't:

- **"Go ahead with this plan?"** Yes or no.
- **Only if no AI reviewer is configured**, in the same prompt: **"Which AI
  reviewer should I set up?"** Cursor Bugbot, GitHub Copilot code review,
  CodeRabbit, or the Claude Code GitHub Action (or none).

Handling the answer:

- **Yes**: go. If no reviewer was picked, set none up and list it as a
  follow-up.
- **No, with changes**: adjust the plan and ask the same question again.
- **A plain no**: stop. The plan stays as audit findings.

After a yes, don't ask anything else.

## Phase 3: Implement (after the yes)

Work in checkpoints and run the relevant gates after each one. Each step wires
its own commands into `check` as it's built, so `check` is green at every
commit.

### 3.0 Branch, gates and formatting

- **Branch**: create `agent-friendly` from the current HEAD, in a new worktree
  if the working tree has uncommitted changes.
- **Commands**: name and invoke them the way the repo's task runner expects;
  `toolchains.md` has an invocation table per runner. Wire `typecheck`,
  `format-check`, `fix`, `lint` (with the current config for now) and the
  existing tests into `check` now. The rest join `check` in the step that
  builds them (table below).
- **Formatter**: if there's none, add the default one. If `format-check` fails
  on the current tree, reformat everything once, in its own commit, so the
  reformat doesn't bury real changes in review.
- **Format on edit**: unless agent edits are already formatted automatically,
  add the `format-changed` script (`checks-and-scripts.md` §4) and register it
  as a post-edit hook for each agent tool in use (`toolchains.md`,
  "Format-on-edit hooks"). Test each hook with a misformatted file. Tools with
  no post-edit hook rely on `fix` and on `format-check` in `check` and CI.
- **AGENTS.md rules**: write the rules half now (layout, dependency rules,
  anatomy, conventions, verification; `contract.md` §2–3). Write anything
  inventory-like later. If a `CLAUDE.md` exists, move anything still true into
  AGENTS.md and delete it.

The full set of roles:

| Role | Does | Added in |
| --- | --- | --- |
| `typecheck` | types or compilation across the whole project | 3.0 |
| `format-check` | the formatter in check mode | 3.0 |
| `fix` | formatter write + linter autofix | 3.0 |
| `lint` | the linter, with warnings failing | 3.0, strict in 3.3 |
| `dev-local` | runs the app with its local services, no secrets (if it runs as a process) | 3.1 |
| `test-baseline` | unit and integration tests, plus the baseline comparison | 3.2 |
| `e2e` | end-to-end flows against keyless local services | 3.2 |
| `check-all` | `check` + `e2e` | 3.2 |
| `structure` | the boundary checker, with `graph` and `owner` modes | 3.4 |
| `check-feature` | `check`, scoped to one feature or path; takes seconds | 3.4 |
| `new-<kind>` | the scaffolder | 3.7 |
| `check` | `typecheck`, `lint`, `format-check`, `structure` and `test-baseline`, cheapest first, failing fast | grows each step |

### 3.1 Keyless local runs

- For each external service, wire its local dev server, emulator, container or
  mock (`toolchains.md`, "Keyless local backends"). `dev-local` starts them
  with the app; `e2e` and integration tests run against them. No keys anywhere.
- Make local runs **parallel-safe**:
  - take ports from env, with a free-port fallback
  - give each worktree its own local database or emulator state, and its own
    temp and build directories (frameworks that lock a build directory need a
    separate one per server)
  - put these directories in the ignore files
- For services with no local option, tests that need them skip locally with a
  conditional skip and a message naming the service, and AGENTS.md lists them
  as cloud-only with the exact command to run them with real keys.
- If a local option exists but its runtime (Docker, a CLI) isn't available on
  this machine, wire it anyway, mark the affected runs as unverified, and say
  so in the final report.
- Verify with `curl` or a smoke test.

### 3.2 Tests first

Before any file moves:

- **Runners**: install the default for each empty role (unit, component, e2e).
  Use what's already there otherwise.
- **Pin today's behaviour**, following the safety-net list from Phase 1:
  - e2e, API or CLI-level tests for each feature's main flows. They go through
    the UI, HTTP or command line, so they don't depend on file paths and stay
    unchanged through the move. They're the main safety net.
  - unit tests for every module headed for core or building blocks, and for
    pure logic the move touches (models, parsers, helpers).
  - test what the code does today, including bugs; list bugs as follow-ups
    rather than fixing them now.
- Put the new tests where the current layout keeps tests (or a top-level
  `tests/` if there are none). They move into feature folders in 3.5.
- Run everything until it's green and stable (run e2e twice to catch flakes).
  Wire `test-baseline`, `e2e` and `check-all`, then commit the tests and the
  baseline (`checks-and-scripts.md` §3). From here on, the count may only go
  up.

### 3.3 Linter and suppressions

Now that tests protect behaviour:

- Switch to the strict config (the framework's preset, warnings failing), and
  triage every finding:
  - fix it properly where you can
  - turn off rules that don't fit the codebase, with the reason as a comment in
    the lint config
  - for deliberate patterns, add a single-line suppression on exactly that line,
    with the reason inline (for example `// eslint-disable-next-line rule --
    reason`, `# noqa: E501  # reason`, `#[allow(x, reason = "…")]`)
- If a legacy codebase has too many reasonless suppressions to triage now,
  grandfather them in a generated allowlist that may only shrink.
- Run the tests after each batch of fixes.

### 3.4 Boundary checker and FEATURE_MAP.md

- Build the checker before migrating, because it's the map you migrate
  against. Include the `graph` (feature dependencies, forward and reverse) and
  `owner` (file → feature and doc) modes: the docs, the review skill and agents
  all rely on them in place of hand-written tables. Rules and output format:
  `checks-and-scripts.md` §2.
- Create `FEATURE_MAP.md` next to AGENTS.md (`contract.md` §5), with every
  planned feature in the "Not yet migrated" table (legacy path → target
  folder), and the same legacy paths in the checker's config. The checker
  ignores legacy directories until they're empty.
- Negative-test every rule: create a violation, confirm it fails with a message
  that says what to do, then remove it.
- Wire `structure`, `check-feature`, `graph` and `owner`; `structure` joins
  `check`.

### 3.5 Migrate feature by feature

Order: core → building blocks → features → composition → thin entry. For each
checkpoint:

1. Move the code with `git mv`, so history survives.
2. Update import paths in code and tests mechanically (with the language
   server, a codemod or the IDE's move refactoring). Change no assertions.
3. Run the typecheck and the full test suite. The e2e tests pass unchanged; the
   unit tests pass with only their imports changed.
4. Move that feature's tests into its folder (the test-placement convention
   from `choosing-structure.md` §7), one test file per module. Tests inside a
   feature import its modules directly; only code outside the feature uses the
   public surface. Run them again: green, and the test count hasn't dropped.
5. Write the feature's `FEATURE.md` (`contract.md` §4: the one-sentence summary
   first, behaviour by sub-feature, `## Files`), and move its row from "Not yet
   migrated" into its table in `FEATURE_MAP.md`.
6. Apply the comments policy to the moved files. Explanations go to:
   user-observable behaviour → `FEATURE.md`; invariants → a test whose name
   states the invariant; tooling reasons → the config file, or AGENTS.md
   "Tooling notes" if there's no config line to put them on. Config files keep
   their comments.
7. Run `check`, then commit the checkpoint.

After the last checkpoint, delete the empty "Not yet migrated" table and run
`check-all` and a build.

- Fix cycles by moving the shared piece down to core, never by widening a rule.
- Never add a type escape or suppression to make a move compile (`toolchains.md`
  lists the syntax per language). Fix the type at its source (for example, by
  moving a shared type to core). If that would change behaviour, leave the file
  where it is, keep it in "Not yet migrated", and list it in the final report.
- Behaviour must not change during the move. If a test fails after a move, the
  move is wrong, not the test.
- Mechanical moves and comment stripping can go to cheaper subagents with exact
  file lists. Verify their output mechanically, with a diff that ignores
  comments, imports and whitespace. Known failure modes: blank lines left where
  comments were (inside type definitions and empty `catch` blocks), behaviour
  "fixed" to satisfy a test, and imports rewritten as deep paths.

### 3.6 Contract docs

Follow `contract.md`:

- finish `AGENTS.md` (aim for under ~150 lines), linking to `FEATURE_MAP.md` at
  the top
- finish `FEATURE_MAP.md`: "Also called", the shared code and building-block
  rows, cross-cutting notes
- nested `AGENTS.md` files for rules that only apply to some paths
- the worked example, or a follow-up if there's no real change to base it on

The governing rule: never write in prose what a command can print or a checker
can verify. When moving existing prose, move it verbatim, then grep the
original lines against the new files to prove nothing was lost.

### 3.7 Scaffolder

Its output must pass every check and follow every convention: agents copy
scaffolded code more than anything else. It takes the feature's one-sentence
summary, writes `FEATURE.md`, adds the `FEATURE_MAP.md` row, and runs
`format-changed` on every file it writes. Spec in `checks-and-scripts.md` §6.

### 3.8 Other scripts

Build the scripts the audit showed a need for (seed/reset, inspect, env-check).
The rules for every script are in `checks-and-scripts.md`.

### 3.9 CI and gate protection

Follow `ci-and-review.md`. CI runs the same `check` command agents run (never a
separate list of steps), plus e2e against the keyless local services. Watch
for the path-filter trap described there. If a CODEOWNERS file exists, add the
gate files (`ci-and-review.md` §3) with its owners.

### 3.10 Review skill and AI reviewer config

Generate a review skill for this repo from `assets/review-skill-template.md`.
Fill it with the repo's commands, docs, nested rules, hotspots, and the
specific hazards the audit found. Put it in the review skill location from the
Defaults. When you're done, grep the result for `{{`: nothing should remain.
Then add thin config for the AI reviewer that's already configured, or the one
picked in Phase 2, as described in `ci-and-review.md`. Reviewers should spend
their budget on what `check` can't see, and any finding that keeps recurring
should become a check.

### 3.11 Coverage on demand

Add `test-coverage`, but not as a gate. Agents run it on the feature they
touched and read the unexecuted lines. A global threshold is easy to game and
slows every run.

## Phase 4: Verify and report

Run these and report the actual numbers:

1. `check`, then `e2e` and a production build where they exist.
2. Tests: the count committed in 3.2 hasn't dropped, every feature has tests in
   its own folder, and the e2e tests passed unchanged through the move.
3. Negative tests: one violation per checker rule. For the baseline, delete a
   test and expect a failure; then lower the number in the baseline file, run
   with `CI=true`, expect a "stale" failure, and restore the file.
4. In a throwaway worktree: scaffold each kind, run the full `check` (it should
   pass), then discard the worktree.
5. `check-feature` on one feature, and `fix` on a deliberately misformatted
   file.
6. Format on edit: feed each configured hook a sample payload pointing at a
   misformatted file, and confirm the file is reformatted.
7. Two `check-all` runs at once, in two worktrees.
8. A `dev-local` smoke test, and e2e with no keys in the environment (or mark
   them unverified if a local runtime was missing).
9. Every new script, with bad arguments (usage is shown) and good arguments.
10. CI: lint the workflow (`actionlint` if available).
11. A review skill dry run, against a small seeded diff with two problems: a
    behaviour change with no `FEATURE.md` update, and a formatting error. Ask
    for early feedback despite the red checks. It passes if the formatting
    error appears only under "Checks" and the `FEATURE.md` gap appears as a
    finding. Revert the diff.
12. AGENTS.md covers: the definition of done, the commands and when to run
    them, scoped runs, the completeness checklist, failure guidance, what can't
    be verified locally, and the worked example (or it's a listed follow-up).
    It contains no counts and no inventories that a command could print.
    `FEATURE_MAP.md` is a separate file with a row for every feature, block and
    core module, and each row tells an agent something the tree can't.
13. `cochange.py . --map <move map>` (the paths in history mapped to the final
    features), so the report has the predicted locality next to today's number.
14. `git status`: clean, on `agent-friendly`, the baseline committed, nothing
    pushed.

Then report:

- what moved where
- tests before vs after, and which flows the new tests pin
- which rules are now enforced, and by which check
- the suppressions triaged and comments removed
- locality before vs predicted after
- the scripts and hooks added, and the reviewer setup
- the calls you made without asking, and why
- anything unverified (missing local runtimes, cloud-only flows)
- follow-ups, each with the exact command or setting: push the branch and open
  a PR; make CI required once it has run on the default branch; CODEOWNERS if
  there was none; installing the AI reviewer or adding its secret; bugs the
  new tests pinned; anything left in "Not yet migrated"

## Principles

- Tests before moves. The e2e tests written first are the proof that the move
  changed nothing.
- The code and its checks are the contract. Prose is the index to them. A
  list in prose is fine only when each item adds something the tree can't show
  (a one-line purpose) and a check keeps the list complete. Counts never are.
- Anything a reviewer flags twice becomes a check.
- One convention per concern beats several reasonable ones.
- Script output is read by an agent with no context. Say what failed, where,
  why, and what to do next.
- Delegate mechanical work, and verify it mechanically.
