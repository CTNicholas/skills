# Choosing the structure

Use this file to decide what the restructured repo should look like. The
examples show resolved layouts for common stacks. They're starting points to
reason from, not templates to copy.

## Contents

1. What the structure is for
2. Classify the repo
3. Find the units
4. The layer ladder
5. Keep the framework's grain
6. Compare candidates on evidence
7. Test placement
8. Sizing: when to do less
9. Patterns to move away from
10. Worked resolutions

## 1. What the structure is for

A good structure gives "where does this change go?" one obvious answer, and
makes that answer checkable by a script. It does this through four
properties:

- **Locality**: a change to one behaviour touches one folder, plus at most a
  one-line registration in the entry layer.
- **Boundaries**: each unit has a public surface, and other code imports only
  that surface.
- **One-way dependencies**: lower layers never import higher ones, and units
  never form cycles.
- **Few hotspots**: no file that every change has to touch.

If a layout choice doesn't improve one of these, it isn't worth the churn.

## 2. Classify the repo

| Archetype           | Typical units                                       | Entry layer                                        | Composition layer                                 |
| ------------------- | --------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------- |
| UI app (web, mobile, desktop) | product features (channels, billing, search) | routes, pages, navigation                           | screens, views and layouts that combine features  |
| Service / API       | domain capabilities (orders, invoices, accounts)    | HTTP/gRPC routes, queue consumers, cron jobs, main | usually none; orchestrators only if a flow spans units |
| CLI                 | commands or groups of capabilities                  | argument parsing, command registration             | none                                              |
| Library / SDK       | public modules (client, auth, retry, models)        | the package's public entry (index, `__init__`, `lib.rs`) | none                                        |
| Monorepo            | packages                                            | `apps/`                                            | apps compose packages                             |
| Data / ML pipeline  | stages or datasets                                  | DAG or job definitions                             | pipelines that compose stages                     |

For a mixed repo, classify each part separately. For example, a Next.js app
with API routes is a UI app whose units also own their server handlers.

## 3. Find the units

Signals, strongest first:

1. **User-visible capabilities**: what a user or PM would name them. Look at
   routes, screens, commands, endpoints, the README feature list and the docs
   navigation.
2. **Co-change clusters** in git history: files that are edited in the same
   commits.
3. **Data ownership**: which code writes which tables, collections, stores or
   state slices.
4. **Existing boundaries**: packages, apps, modules or contexts that already
   exist.

Test each candidate:

- Can you describe it in one user-facing sentence?
- Could one agent own it for a week while touching only its folder (plus at
  most a one-line registration in the entry layer)?
- Does it own the writes to its data, with other code reading through its
  public surface?

If a candidate is **too small** (one component with no behaviour of its own),
fold it into a neighbouring unit or make it a building block. If it's **too
big** (its doc needs more than ~8 sub-features, or its folder has more than
~15–20 files), split it by sub-capability.

**When signals disagree**: in a service, data ownership wins (a unit owns the
writes to its data). In a UI app, user vocabulary wins (a unit is what users
would call a feature). Co-change history breaks the remaining ties.

**Naming**: use the product's vocabulary and the language's convention. That
means kebab-case folders in JS/TS, snake_case packages in Python and Rust
modules, short lowercase package names in Go, and lowercase packages on the JVM.
Don't rename existing units whose names already fit; renames cost history and
churn.

**Cross-cutting concerns**:

| Concern                                  | Usually goes in                                                         |
| ---------------------------------------- | ----------------------------------------------------------------------- |
| Auth and session                         | core, or its own unit if it has screens or behaviour                     |
| Logging, config, ids, errors, API clients | core                                                                    |
| Design system and generic UI             | building blocks                                                          |
| Server handlers for a feature            | inside the owning unit, in a server-only subfolder                       |
| i18n catalogues                          | per unit if the framework allows it; otherwise one file, flagged as a hotspot |
| Feature flags and analytics              | core for the client; each unit owns its own events and flags             |
| Database migrations                      | where the framework expects them (often one folder, an append-only hotspot that's acceptable); exempt from unit file lists |
| Generated code (API clients, ORM types, protobuf) | next to its consumer, or in core if shared; never hand-edited; excluded from formatting, comments and file-list rules |
| Vendored code                            | its own top-level folder, excluded from every rule                       |

## 4. The layer ladder

Each layer imports only from itself or the layers below it:

```
entry → composition → units → building blocks → core
```

| Layer           | Holds                                                         | Common names                                                                                     |
| --------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| entry           | framework and process entry points; wires things up and delegates | `app/`, `pages/`, `routes/`, `cmd/`, `bin/`, `main.py`, `src/main.rs`, `config/routes.rb`      |
| composition     | screens, layouts and workflows that combine units             | `views/`, `screens/`, `layouts/`, `flows/`                                                       |
| units           | vertical slices that own a behaviour end to end               | `features/`, `modules/`, `domains/`, Django apps, Phoenix contexts, packwerk packs, `internal/<x>` (Go), workspace crates or packages |
| building blocks | reusable pieces with no domain knowledge                      | `primitives/`, `ui/`, `components/ui/`, `adapters/`                                              |
| core            | shared model, helpers, types, config, clients                 | `lib/`, `core/`, `shared/`, `platform/`, `internal/platform/`                                    |

Rules that hold in every stack:

- **Units import other units only through their public surface**, and never in
  a cycle. When a cycle appears, the shared piece moves down to core.
- **A building block is promoted only on its second use.** The first use stays
  inside the unit that needs it.
- **Core imports nothing above itself** and contains no UI.
- **Entry is thin.** A route file re-exports or calls one handler, and any logic
  in the entry layer is a review finding.
- **Server-only code** (handlers, secrets, database access) stays out of any
  public surface that client code imports.
- **Shared test infrastructure** (setup, fakes, mocks, fixtures, e2e helpers)
  lives in one place, and production code never imports it.

Drop the layers the repo doesn't need. If no screen combines units, there's no
composition layer. If nothing is reused, there are no building blocks. A tiny
repo may need only units and core.

## 5. Keep the framework's grain

Agents and humans both expect the ecosystem's conventions, and fighting a
framework means every generator, doc and tutorial works against you.

| Situation                                                                                         | Do                                                                                                                      |
| ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| The framework requires certain directories (Next `app/`, Expo `app/`, SvelteKit `src/routes`, Nuxt `pages/`, Rails `app/*`) | Treat them as the entry layer and keep them thin                                                       |
| The language enforces boundaries (Go packages and `internal/`, Rust crates, JVM modules, .NET projects, SwiftPM targets) | Make those the units; most enforcement comes free, so add checks only for what the compiler doesn't cover |
| The framework has a module concept (Django apps, NestJS modules, Angular feature areas, Phoenix contexts, Rails engines or packwerk packs) | Make those the units, and enforce them with the ecosystem's tool                          |
| It's a workspace monorepo                                                                         | Packages are the units, and declared dependencies are the layer rules; add layering inside a package only when it's large |
| The convention is technical layering (Rails MVC, classic MVC .NET)                                | Don't rewrite into `features/` wholesale. For large apps, introduce boundaries with the ecosystem's modularisation tool; for small ones, keep the layout and add the contract, checks and CI |

## 6. Compare candidates on evidence

An agent left to itself will usually propose the full ladder. Make the choice on
evidence instead.

1. **Always include "keep the layout, add the contract"** (AGENTS.md, `check`,
   CI, the review skill). It costs nothing in churn, and sometimes it's enough.
2. **Write one or two restructure candidates as map files.** A map file assigns
   paths, as they appear in git history, to proposed units. Globs are relative
   to `--root` if you use it, are matched in order (first match wins), and use
   fnmatch, so `*` also crosses `/`. Names starting with `_` are layers or
   files that a feature change may legitimately touch (entry registrations,
   docs), and they aren't counted:

   ```json
   {
     "channels": ["components/channel-*", "lib/channels.ts", "tests/channels*"],
     "messages": ["components/composer*", "components/message-*", "lib/messages.ts"],
     "core": ["lib/*"],
     "_entry": ["app/*"],
     "_docs": ["*.md"]
   }
   ```

3. **Score each one** with `cochange.py . --map <file>` (pass `--map` more than
   once to compare candidates). It replays recent commits and reports, on the
   same basis, the share that touched exactly one area today and the share that
   would have touched exactly one unit. It also lists the most common
   multi-unit combinations, and any unmapped files (which are scored by their
   current area). How to read a recurring combination:
   - **Two units together**: the boundary is in the wrong place. Merge them, or
     move what they share into core.
   - **A unit plus core**: the piece probably belongs in the unit, or core's
     API is still changing. Moving more into core would make this worse.
4. **Weigh it against the cost**:
   - files moved
   - open branches and PRs that will conflict
   - generators and docs that will fight the framework
   - how much the team already knows the current layout

   Recommend a restructure only when it beats today's locality by a clear
   margin (about 15 points or more as a rule of thumb) and the user accepts the
   disruption. Show the numbers in the report either way.

Keep the map files in a scratch location, not in the repo.

## 7. Test placement

Pick one rule, enforce it, and fit it to the language:

| Ecosystem | Convention                                                                                                   |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| Go        | `_test.go` files beside the code (the toolchain requires this for package-internal tests); shared helpers in `internal/testutil` |
| Rust      | inline `#[cfg(test)] mod tests` for unit tests; each crate's `tests/` for integration tests                   |
| JVM       | `src/test/...` mirroring the packages                                                                         |
| .NET      | one test project per unit project                                                                             |
| Python    | a `tests/` folder in each unit package, or a top-level `tests/` mirroring the units. Pick one. (With duplicate basenames, use pytest's `--import-mode=importlib`.) |
| JS/TS     | a `tests/` folder in each unit (keeps the folder listing readable), or sibling `*.test.ts` files. Pick one.   |
| Ruby      | `spec/` mirroring, or a `spec/` per pack                                                                     |
| Elixir    | `test/` mirroring                                                                                             |

Give each runner its own suffix or directory (for example, `.test.` for unit
tests and `.spec.` for e2e in JS, or `tests/unit/` and `tests/integration/` in
Python) so each runner only picks up its own files.

## 8. Sizing: when to do less

| Repo                                        | Propose                                                                                                                          |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Under ~30 source files, 1–3 capabilities     | Units + core (or keep it flat), `check`, CI, a short AGENTS.md and a review skill. Usually skip composition, building blocks and the scaffolder, and put the features table in AGENTS.md instead of a separate feature map. |
| A typical app (~30–500 files)               | The parts of the ladder it needs, and the full contract                                                                          |
| Large, or a monorepo                        | A contract per package (nested AGENTS.md), a root contract for cross-package rules only, affected-only checks, and an incremental migration |

If a full restructure is too risky right now, the contract, `check` and CI pay
off on their own. Propose those first, then migrate one unit per PR.

## 9. Patterns to move away from

- **Technical top-level folders for every feature** (`components/`, `hooks/`,
  `services/`, `utils/`): every feature change touches four folders, and every
  agent collides with every other agent.
- **`utils/` or `helpers/` junk drawers**: split them into core modules by
  topic, each with a test.
- **One central types file, constants file or route table that everyone
  edits**: split it per unit, or generate it.
- **Wildcard re-exports** (`export *`, `from x import *`): the public surface
  silently becomes everything.
- **A "common" unit that imports units back**: that's a cycle in disguise.
- **Deep imports into another unit's internals.**
- **Global stylesheets shared by every feature**: scope styles to the unit.

## 10. Worked resolutions

These show how the ladder resolves in different stacks. Adapt names to what
the repo already uses.

**Next.js app router, realtime messaging app** (the case this skill was first
built on):

```
app/          entry: routing only; app/api/**/route.ts is one line re-exporting a handler
views/        composition: screen regions (sidebar, conversation, thread panel)
features/     units: channels, messages, threads, reactions, presence…
              each has index.ts (named exports only, never ./api), FEATURE.md, api/, tests/
primitives/   building blocks: avatar, button, popover (promoted on second use)
lib/          core: ids, guards, formatting, shared types
tests/        shared test infrastructure only (setup, backend mock, e2e helpers)
scripts/      check-structure, check-test-baseline, scaffold
```

The app imports `views/` barrels, and route files deep-import
`features/<f>/api/<handler>` (the one allowed deep import). Tests go in
`tests/` beside the code: `.test.` for Vitest, `.spec.` for Playwright.

**Go HTTP service**:

```
cmd/api/main.go           entry: config, wiring, start the server
internal/http/            entry: routes → unit handlers, nothing else
internal/orders/          unit: handler.go, service.go, store.go, *_test.go, FEATURE.md
internal/invoices/        unit
internal/platform/        core: db, logging, config, ids
```

The compiler forbids cycles. Use depguard (in golangci-lint) to stop units from
importing `internal/http` and to stop `platform` from importing any unit. Keep
exported identifiers' doc comments, because Go tooling relies on them.

**Python FastAPI service**:

```
src/app/main.py               entry: app factory, router includes
src/app/features/orders/      unit: __init__.py (public surface, explicit __all__),
                              router.py, service.py, models.py, repository.py, FEATURE.md, tests/
src/app/core/                 core: db session, settings, auth dependencies, errors
```

Use an import-linter layers contract (`main → features → core`). Add a repo
script that only allows cross-feature imports through `features.<x>` (the
`__init__`).

**Django**: the apps are the units. The project package (settings, root URLs)
is the entry layer, and a `core` app holds shared code. Keep Django's layout,
and enforce app boundaries with import-linter.

**Rails**: for a small app, keep MVC and add the contract, checks, CI and
review skill. For a large app, use packwerk packs (`packs/<unit>/` with its
own `app/` and `spec/`) and declare dependencies in `package.yml`.

**pnpm + Turborepo monorepo**:

```
apps/web, apps/api        entry + composition
packages/<unit>           units, each with its own AGENTS.md, check script and tests
packages/ui               building blocks
packages/core             core
```

The layer rules are the declared workspace dependencies. Root `check` runs only
affected packages (`turbo run check --affected`), and CI runs the same command.

**Rust CLI**: `src/main.rs` holds argument parsing (entry),
`src/commands/<cmd>.rs` holds thin command handlers, `src/<unit>/` modules hold
the behaviour, and `src/core/` holds shared code. Split into workspace crates
only when compile times or boundaries demand it; then the crate graph becomes
the layer rule.

**TypeScript SDK (library)**: `src/index.ts` is the public API (entry),
`src/<module>/` are the units, and `src/internal/` is core. Add a public-API
snapshot check (for example, API Extractor) so that breaking changes become a
check failure rather than something a reviewer has to notice. The equivalents
elsewhere are `cargo-semver-checks` for Rust and `griffe check` for Python.
