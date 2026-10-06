# Checks and scripts

## Contents

1. Rules for every script
2. The boundary checker
3. Test baseline
4. Scoped check and fix
5. Scaffolder
6. Graph and owner lookups
7. Other candidate scripts

## 1. Rules for every script

Every script is a tool an agent will call blind, from a prompt. Build each one
so that a single run answers the question or does the job, and the output
explains itself.

- **No extra dependencies**: use the repo's primary language and its standard
  library (`toolchains.md`), so the script never breaks on a dependency bump.
- **One concern per script**, exposed through the task runner and named the
  way that runner expects (`toolchains.md`). For example, npm uses
  `lint:structure` and just uses `check-unit`. Agents find commands in the task
  runner, not by reading `scripts/`.
- **Exit code 0 or 1, and nothing else.**
  - Each failure prints one line in the form `path:line: rule-id — what's
    wrong. Fix: what to do.`, then a count of failures.
  - Success prints one line with the numbers checked (`Structure check passed
    (113 files, 9 units)`). Never exit silently.
- **Print the next steps** when the script can't finish the job itself. Prefer
  having the checker enforce a step over having a script edit shared files,
  which is fragile. The one exception is inserting a single sorted row, like
  the scaffolder's feature-map row (section 5).
- **Validate inputs** (names that follow the language's naming convention, a
  unit that exists) and print usage on bad arguments. Refuse to overwrite files. Be idempotent where possible.
- **Deterministic and fast** (a few seconds at most), so the script can sit
  inside `check`.
- **No secrets and no network**, unless that's the script's whole purpose.
  Derive everything from the tree and from machine-readable tool output.
- **Negative-test it**: create the condition it should catch, confirm it fails,
  then remove the condition. A checker that has never failed has never been
  tested.
- **Document it in AGENTS.md** with one line: command, purpose, when to run it.
- **Keep policy out of prose**: if a rule matters, a script enforces it.

## 2. The boundary checker

Exposed as the `structure` role (`lint:structure` in npm). Keep its settings
(layers, unit roots, allowed deep imports, exemptions, sync pairs) in a small
config block at the top of the script or in a JSON file next to it, so a rule
change is a reviewable one-line diff. Where an ecosystem tool handles import rules well
(import-linter, depguard, ArchUnit, packwerk, deptrac, dependency-cruiser), use
it for those rules and keep the repo script for the rest. Both run under the
same command.

### Rules

Implement the rules that apply to the approved structure.

| Rule id            | Enforces                                                                                                   |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| `layer`            | Import direction between layers. Resolve aliases and relative imports to a real path first.                |
| `public-surface`   | Code outside a unit imports only that unit's public surface. List any allowed deep imports explicitly in the config (for example, route files importing server handlers). |
| `cycle`            | No cycles between units (a DFS over unit → unit edges). Only Go packages and Cargo crates get this for free: modules inside one crate, package or JVM module can still form cycles. |
| `surface-shape`    | The public surface is explicit: no `export *`, no `from x import *`, and an explicit `__all__` where the language has one. In codebases where client and server code share a tree, nothing server-only is re-exported into a surface that client code imports. |
| `test-infra`       | Production code never imports shared test infrastructure (fakes, mocks, helpers).                           |
| `anatomy`          | Every unit has its required files: public surface, a non-empty test folder (or test files), and a non-empty unit doc. |
| `test-placement`   | Tests follow the chosen convention, and no test file sits outside it. Every core and building-block module has a matching test, meaning a test file named after the module in the conventional place. Type-only, constants-only and config modules can be exempted in the config, by name. |
| `feature-map`      | Every unit, composition piece, building block and core module has exactly one row in the feature map, and every link resolves. Match paths exactly, so `features/chat/FEATURE.md` doesn't also match `features/chat-admin/`. Each unit's summary equals the first line of its doc (ignoring whitespace). Rows are sorted within each table. The "Not yet migrated" table matches the legacy directories in the checker's config. Spec in `contract.md` §5. |
| `unit-files`       | Each unit doc's `## Files` section lists exactly the files in the unit folder, recursively, checked both ways. Excluded: generated files, snapshots, and files the language requires but that carry no logic (such as an empty `__init__.py`). Homogeneous folders (`migrations/`, `fixtures/`) may be listed as one directory entry. |
| `suppressions`     | Every suppression in code (lint disables, `@ts-expect-error`, `# type: ignore`, `#[allow]`, `//nolint`; syntax per language in `toolchains.md`) carries an inline reason. Type escapes (`as any`, `cast`, `!`) aren't suppressions: ban the risky ones with a lint rule, or leave them to review. Where the tool supports a reason field (`-- reason` in ESLint, `reason = "…"` in Rust), use it; otherwise use a trailing comment. A legacy allowlist, if one exists, may only shrink. |
| `comments`         | If a comments policy is adopted, it covers source files only. Under "none", the only comments allowed are suppressions (with their same-line reason) and magic comments, both listed in `toolchains.md`. Under "public API docs only", doc comments on exported items are also allowed (docstrings, `///`, Javadoc, Go doc comments). Use the language's tokenizer where it ships one. |
| `legacy`           | Removed directories (`components/`, `utils/`, `tests/unit/`…) must not reappear.                           |
| `conventions`      | Repo-specific rules the audit found and the user approved. For example: no `data-testid` outside tests, no `.only` or `.skip` committed, no `process.env` outside the config module, no `console.log` in production code. |
| `sync`             | Named blocks copied between files stay identical. Each block sits between `<!-- sync:<name>:start -->` and `<!-- sync:<name>:end -->`, and the config lists its source and its copies. Compare the lines between the markers after stripping leading whitespace. Used for the completeness checklist, the review hazards, and scoped rules copied for a second tool (`contract.md`, `ci-and-review.md`). |
| `size` (warn)      | Source files over ~300 lines are listed as warnings, without failing (tests and generated files excluded). Guidance: one main concept per file; move pure logic into its own module. Alternatively, a ratchet: existing large files may shrink but not grow. |

### Messages that say what to do

Every message names the fix, not just the rule:

```
features/chat/composer.tsx:12: layer — features/ may not import views/conversation. Fix: move the shared piece to lib/, or pass it in as a prop.
views/sidebar/sidebar.tsx:8: public-surface — imports features/channels/channel-row (internal). Fix: export ChannelRow from features/channels/index.ts and import it from there.
src/app/features/billing/service.py:4: public-surface — imports app.features.orders.repository (internal). Fix: add what you need to app/features/orders/__init__.py and __all__, then import from app.features.orders.
internal/platform/db/tx.go:9: layer — platform may not import internal/orders. Fix: move the shared type into internal/platform, or invert the dependency with an interface.
features/search/FEATURE.md: unit-files — search-input.tsx exists but isn't listed under ## Files. Fix: add it with a one-line purpose.
FEATURE_MAP.md: feature-map — features/reactions has no row. Fix: add `| [reactions](features/reactions/FEATURE.md) | <first line of its FEATURE.md> | |` to the Features table, in sorted position.
FEATURE_MAP.md:14: feature-map — the summary for channels differs from the first line of features/channels/FEATURE.md. Fix: decide which one is right, then make them match.
src/app/core/cache.py:31: suppressions — `# type: ignore` has no reason. Fix: fix the type, or write `# type: ignore[code]  # <why>`.
```

### Modes

These are required: the docs and the review skill call them in place of
hand-written tables. Expose them as their own task-runner commands (`graph`,
`owner`).

- `--graph`: prints all unit → unit edges, which the checker computes anyway.
- `--graph <unit>`: prints what one unit depends on.
- `--graph <unit> --reverse`: prints who depends on that unit, which is what
  breaks if its public surface changes.
- `--owner <path>…`: prints the owning unit (or layer) and its doc for each
  path.

### During migration

Rules apply only to directories in the new structure. Legacy directories are
ignored until they're empty, and then they're added to the `legacy` rule.

## 3. Test baseline

Exposed as the `test-baseline` role (`test:baseline` in npm).

- A committed file (for example, `tests/baseline.json`) holds
  `{ "<runner>": { "files": n, "tests": n } }` for each runner.
- Run the tests with the runner's machine-readable output and read the counts
  (`toolchains.md` lists the fields for each runner). For e2e runners with a
  `--list` mode, use it, so the count needs no browser.
- **Fewer than the baseline → fail** with: "tests may only be removed
  deliberately; lower the baseline by hand and say so in the PR".
- **More than the baseline, run locally → rewrite the file** and print
  "baseline raised to N; commit tests/baseline.json".
- **More than the baseline, run in CI (`CI` env var set) → fail** with "stale
  baseline: run `<test-baseline>` locally and commit the file". Otherwise
  nothing makes anyone commit the higher count, and the ratchet slips.
- `--check` never writes, in any environment. Use it during audits and anywhere
  the tree must stay untouched.
- Never repeat the counts in prose.
- **Parallel agents**: two branches that both add tests will conflict on this
  file. The documented resolution is to take the larger numbers, then rerun
  `test-baseline`. In high-concurrency repos, CI can instead compare the head
  count with the base branch's count, and skip the committed file entirely.

## 4. Scoped check and fix

- **`check-unit <unit|path>`** is a small script, not a chained task (most
  runners can't pass an argument to every step of a chain). It resolves the
  argument to a unit folder, then runs:
  - the linter, formatter check and tests, limited to that folder
  - the full structure check (it's fast, and boundaries are global)
  - the typecheck, incrementally if the toolchain supports it

  It ends with: "Scoped check passed. Run `<check>` before declaring done." The
  point is a loop of seconds, because agents run fast loops far more often than
  slow ones.
- **`fix`** runs the formatter in write mode, then the linter's autofix, over
  the whole repo or a given path. The contract tells agents never to
  hand-format, so give them the one command that does it for them.

## 5. Scaffolder

Exposed as `new-<kind> <name> "<one sentence>"`, named per runner (for example
`npm run new:feature -- reactions "React to a message with an emoji and see who
reacted."`, or `just new-module orders "Place, track and cancel orders."`).

- Validate the name against the language's naming convention, derive any other
  casings (such as PascalCase) from it, and refuse to overwrite anything.
- Require the one-sentence summary, and refuse to run without it. Every unit
  must be describable in one sentence a user would understand (Phase 1), and
  the sentence is needed in two places.
- Generate the full anatomy: public surface, one main file, a test that passes
  and asserts something real, and a unit doc from the template, with the
  summary as its first line and its `## Files` filled in.
- Insert the unit's row into the feature map, in sorted position, with an empty
  "Also called". If the table can't be found, print the exact row to add, and
  exit non-zero.
- **The output must pass every check and follow every convention.** If the
  contract prefers role or label queries over test ids, the generated test uses
  a role query. If comments are banned, the template has none. Scaffolded code
  is the example agents copy most, so one wrong convention there spreads to
  every new unit.
- Print the remaining steps: fill in "Also called" if users have another name
  for it, describe the behaviour in the unit doc, import the unit only through
  its public surface, run `check`.
- Verify by scaffolding, running the full `check`, then deleting. A
  `check-scaffold` step can do the same in a temporary directory in CI, so the
  templates can't drift away from the rules.

## 6. Graph and owner lookups

These replace hand-maintained tables:

| Question an agent has                         | Command                    | Replaces                                  |
| --------------------------------------------- | -------------------------- | ----------------------------------------- |
| Which unit owns this file, and which doc should I update? | `owner <path>`   | ownership columns in docs                 |
| What does this unit depend on?                | `graph <unit>`             | "may import from" columns                 |
| What breaks if I change this unit's public surface? | `graph <unit> --reverse` | guessing                                |

## 7. Other candidate scripts

Propose only the ones the audit shows a need for. Leave out anything the
framework or test runner already does well.

| Script             | Answers or does                                                     |
| ------------------ | ------------------------------------------------------------------- |
| `dev-local`        | Runs the app with no secrets (when it runs as a process)            |
| `seed` / `reset`   | Puts the local backend or database into a known state for manual checks |
| `inspect <id>`     | Dumps backend state (rooms, documents, rows, queues) for debugging   |
| `env-check`        | Lists which env vars are set or missing, and what each one unlocks   |
| `test-coverage`    | Coverage for one unit, run on demand, never as a gate               |
