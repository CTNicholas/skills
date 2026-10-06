# Choosing the structure

Use this file to decide what the restructured repo looks like. Every feature
gets its own folder; this file is about which features, where the lines go,
and what to call things in each stack. The examples show resolved layouts for
common stacks. They're starting points to reason from, not templates to copy.

A "feature folder" takes the ecosystem's form: a `features/<name>/` folder in
most JS/TS and Python apps, a package in Go, a crate or module in Rust, a
Django app, a packwerk pack, a workspace package in a monorepo.

## Contents

1. What the structure is for
2. Classify the repo
3. Find the features
4. The layer ladder
5. Keep the framework's grain
6. Draw the boundaries on evidence
7. Test placement
8. Sizing
9. Patterns to move away from
10. Worked resolutions

## 1. What the structure is for

A good structure gives "where does this change go?" one obvious answer, and
makes that answer checkable by a script. It does this through four
properties:

- **Locality**: a change to one behaviour touches one folder, plus at most a
  one-line registration in the entry layer.
- **Boundaries**: each feature has a public surface, and other code imports
  only that surface.
- **One-way dependencies**: lower layers never import higher ones, and
  features never form cycles.
- **Few hotspots**: no file that every change has to touch.

## 2. Classify the repo

| Archetype | Typical features | Entry layer | Composition layer |
| --- | --- | --- | --- |
| UI app (web, mobile, desktop) | product features (channels, billing, search) | routes, pages, navigation | screens, views and layouts that combine features |
| Service / API | domain capabilities (orders, invoices, accounts) | HTTP/gRPC routes, queue consumers, cron jobs, main | usually none; orchestrators only if a flow spans features |
| CLI | commands or groups of capabilities | argument parsing, command registration | none |
| Library / SDK | public modules (client, auth, retry, models) | the package's public entry (index, `__init__`, `lib.rs`) | none |
| Monorepo | packages | `apps/` | apps compose packages |
| Data / ML pipeline | stages or datasets | DAG or job definitions | pipelines that compose stages |

For a mixed repo, classify each part separately. For example, a Next.js app
with API routes is a UI app whose features also own their server handlers.

## 3. Find the features

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
fold it into a neighbouring feature or make it a building block. If it's **too
big** (its FEATURE.md needs more than ~8 sub-features, or its folder has more
than ~15–20 files), split it by sub-capability.

**When signals disagree**: in a service, data ownership wins (a feature owns
the writes to its data). In a UI app, user vocabulary wins (a feature is what
users would call a feature). Co-change history breaks the remaining ties.

**Naming**: use the product's vocabulary and the language's convention. That
means kebab-case folders in JS/TS, snake_case packages in Python and Rust
modules, short lowercase package names in Go, and lowercase packages on the JVM.
Don't rename existing modules whose names already fit; renames cost history
and churn.

**Cross-cutting concerns**:

| Concern | Usually goes in |
| --- | --- |
| Auth and session | core, or its own feature if it has screens or behaviour |
| Logging, config, ids, errors, API clients | core |
| Design system and generic UI | building blocks |
| Server handlers for a feature | inside the owning feature, in a server-only subfolder |
| i18n catalogues | per feature if the framework allows it; otherwise one file, flagged as a hotspot |
| Feature flags and analytics | core for the client; each feature owns its own events and flags |
| Database migrations | where the framework expects them (often one folder, an append-only hotspot that's acceptable); exempt from feature file lists |
| Generated code (API clients, ORM types, protobuf) | next to its consumer, or in core if shared; never hand-edited; excluded from formatting, comments and file-list rules |
| Vendored code | its own top-level folder, excluded from every rule |

## 4. The layer ladder

Each layer imports only from itself or the layers below it:

```
entry → composition → features → building blocks → core
```

| Layer | Holds | Common names |
| --- | --- | --- |
| entry | framework and process entry points; wires things up and delegates | `app/`, `pages/`, `routes/`, `cmd/`, `bin/`, `main.py`, `src/main.rs`, `config/routes.rb` |
| composition | screens, layouts and workflows that combine features | `views/`, `screens/`, `layouts/`, `flows/` |
| features | one folder per feature, owning its behaviour end to end | `features/`, Django apps, Phoenix contexts, packwerk packs, `internal/<x>` (Go), workspace crates or packages |
| building blocks | reusable pieces with no domain knowledge | `primitives/`, `ui/`, `components/ui/`, `adapters/` |
| core | shared model, helpers, types, config, clients | `lib/`, `core/`, `shared/`, `platform/`, `internal/platform/` |

Rules that hold in every stack:

- **Features import other features only through their public surface**, and
  never in a cycle. When a cycle appears, the shared piece moves down to core.
- **A building block is promoted only on its second use.** The first use stays
  inside the feature that needs it.
- **Core imports nothing above itself** and contains no UI.
- **Entry is thin.** A route file re-exports or calls one handler, and any logic
  in the entry layer is a review finding.
- **Server-only code** (handlers, secrets, database access) stays out of any
  public surface that client code imports.
- **Shared test infrastructure** (setup, fakes, mocks, fixtures, e2e helpers)
  lives in one place, and production code never imports it.

Drop the layers the repo doesn't need, except features. If no screen combines
features, there's no composition layer. If nothing is reused, there are no
building blocks.

## 5. Keep the framework's grain

Agents and humans both expect the ecosystem's conventions, and fighting a
framework means every generator, doc and tutorial works against you. Feature
folders take the framework's form:

| Situation | Do |
| --- | --- |
| The framework requires certain directories (Next `app/`, Expo `app/`, SvelteKit `src/routes`, Nuxt `pages/`, Rails `app/*`) | Treat them as the entry layer and keep them thin; behaviour moves into feature folders |
| The language enforces boundaries (Go packages and `internal/`, Rust crates, JVM modules, .NET projects, SwiftPM targets) | Feature folders take that form, one package, crate or project per feature; split any that are technical layers (`handlers`, `services`) or hold several features. Most enforcement comes free, so add checks only for what the compiler doesn't cover |
| The framework has a module concept (Django apps, NestJS modules, Angular feature areas, Phoenix contexts, Rails engines or packwerk packs) | Feature folders take that form, one per feature (split a single app that holds everything), enforced with the ecosystem's tool |
| It's a workspace monorepo | Packages are the top-level units, and declared dependencies are the layer rules; inside an app package, features get folders as usual |
| The convention is technical layering (Rails MVC, classic MVC .NET) | Move to the ecosystem's feature-folder form: packwerk packs for Rails, feature folders (vertical slices) for .NET MVC |

## 6. Draw the boundaries on evidence

Every feature gets its own folder; the evidence decides where the lines go.

1. **Write one or two candidate maps.** A map file assigns paths, as they
   appear in git history, to proposed features. Globs are relative to `--root`
   if you use it, are matched in order (first match wins), and use fnmatch, so
   `*` also crosses `/`. Names starting with `_` are layers or files that a
   feature change may legitimately touch (entry registrations, docs), and they
   aren't counted:

   ```json
   {
     "channels": ["components/channel-*", "lib/channels.ts", "tests/channels*"],
     "messages": ["components/composer*", "components/message-*", "lib/messages.ts"],
     "core": ["lib/*"],
     "_entry": ["app/*"],
     "_docs": ["*.md"]
   }
   ```

2. **Score them** with `cochange.py . --map <file>` (pass `--map` more than
   once to compare). It replays recent commits and reports, on the same basis,
   the share that touched exactly one area today and the share that would have
   touched exactly one feature. It also lists the most common multi-feature
   combinations, and any unmapped files (scored by their current area).
3. **Pick the best-scoring map, then fix its boundaries.** How to read a
   recurring combination:
   - **Two features together**: the boundary is in the wrong place. Merge them,
     or move what they share into core.
   - **A feature plus core**: the piece probably belongs in the feature, or
     core's API is still changing. Moving more into core would make this worse.
4. **Report** today's locality and the predicted locality in the plan.

Keep the map files in a scratch location, not in the repo.

## 7. Test placement

Pick one rule, enforce it, and fit it to the language. The tests written first
(Phase 3.2) move into this layout as each feature moves.

| Ecosystem | Convention |
| --- | --- |
| Go | `_test.go` files beside the code (the toolchain requires this for package-internal tests); shared helpers in `internal/testutil` |
| Rust | inline `#[cfg(test)] mod tests` for unit tests; each crate's `tests/` for integration tests |
| JVM | `src/test/...` mirroring the packages |
| .NET | one test project per feature project |
| Python | a `tests/` folder in each feature package |
| JS/TS | a `tests/` folder in each feature (keeps the folder listing readable) |
| Ruby | a `spec/` per pack |
| Elixir | `test/` mirroring the contexts |

E2E tests for a feature's flows live in that feature's `tests/` folder where
the runner allows it; otherwise in one e2e folder with a file per feature.
Shared e2e helpers go in the shared test infrastructure folder.

Give each runner its own suffix or directory (for example, `.test.` for unit
tests and `.spec.` for e2e in JS, or `tests/unit/` and `tests/e2e/` in Python)
so each runner only picks up its own files.

## 8. Sizing

The core never shrinks: feature folders, FEATURE_MAP.md, AGENTS.md, FEATURE.md
per feature, tests, `check`, format on edit, CI and a review skill. What scales:

| Repo | Extras |
| --- | --- |
| Under ~30 source files | Features + core only; usually no composition or building-block layers, and a single scaffold kind |
| A typical app (~30–500 files) | The layers it needs, scaffold kinds per layer, extra scripts where the audit found toil |
| Very large, or a monorepo | A contract and FEATURE_MAP.md per package, a root contract for cross-package rules, affected-only checks, and a migration split across PRs (gates, tests and the first features first) |

## 9. Patterns to move away from

- **Technical top-level folders for every feature** (`components/`, `hooks/`,
  `services/`, `utils/`): every feature change touches four folders, and every
  agent collides with every other agent.
- **`utils/` or `helpers/` junk drawers**: split them into core modules by
  topic, each with a test.
- **One central types file, constants file or route table that everyone
  edits**: split it per feature, or generate it.
- **Wildcard re-exports** (`export *`, `from x import *`): the public surface
  silently becomes everything.
- **A "common" feature that imports features back**: that's a cycle in
  disguise.
- **Deep imports into another feature's internals.**
- **Global stylesheets shared by every feature**: scope styles to the feature.

## 10. Worked resolutions

These show how the ladder resolves in different stacks. Adapt names to what
the repo already uses.

**Next.js app router, realtime messaging app** (the case this skill was first
built on):

```
app/          entry: routing only; app/api/**/route.ts is one line re-exporting a handler
views/        composition: screen regions (sidebar, conversation, thread panel)
features/     channels, messages, threads, reactions, presence…
              each has index.ts (named exports only, never ./api), FEATURE.md, api/, tests/
primitives/   building blocks: avatar, button, popover (promoted on second use)
lib/          core: ids, guards, formatting, shared types
tests/        shared test infrastructure only (setup, backend mock, e2e helpers)
scripts/      check-structure, check-feature, check-test-baseline, scaffold, format-changed
AGENTS.md     the contract
FEATURE_MAP.md
```

The app imports `views/` barrels, and route files deep-import
`features/<f>/api/<handler>` (the one allowed deep import). Tests go in
`tests/` beside the code: `.test.` for Vitest, `.spec.` for Playwright.

**Go HTTP service**:

```
cmd/api/main.go           entry: config, wiring, start the server
internal/http/            entry: routes → feature handlers, nothing else
internal/orders/          feature: handler.go, service.go, store.go, *_test.go, FEATURE.md
internal/invoices/        feature
internal/platform/        core: db, logging, config, ids
```

The compiler forbids cycles. Use depguard (in golangci-lint) to stop features
from importing `internal/http` and to stop `platform` from importing any
feature. Keep exported identifiers' doc comments, because Go tooling relies on
them.

**Python FastAPI service**:

```
src/app/main.py               entry: app factory, router includes
src/app/features/orders/      feature: __init__.py (public surface, explicit __all__),
                              router.py, service.py, models.py, repository.py, FEATURE.md, tests/
src/app/core/                 core: db session, settings, auth dependencies, errors
```

Use an import-linter layers contract (`main → features → core`). Add a repo
script that only allows cross-feature imports through `features.<x>` (the
`__init__`).

**Django**: the apps are the feature folders. The project package (settings,
root URLs) is the entry layer, and a `core` app holds shared code. Enforce app
boundaries with import-linter.

**Rails**: packwerk packs (`packs/<feature>/` with its own `app/`, `spec/` and
FEATURE.md), with dependencies declared in `package.yml`. Rails' own `app/`
keeps only what the framework needs at the top level.

**pnpm + Turborepo monorepo**:

```
apps/web, apps/api        entry + composition; each app has features/ inside
packages/<name>           shared packages, each with its own AGENTS.md, FEATURE_MAP.md, check script and tests
packages/ui               building blocks
packages/core             core
```

The package layer rules are the declared workspace dependencies. Root `check`
runs only affected packages (`turbo run check --affected`), and CI runs the
same command.

**Rust CLI**: `src/main.rs` holds argument parsing (entry),
`src/commands/<cmd>.rs` holds thin command handlers, `src/<feature>/` modules
hold the behaviour, and `src/core/` holds shared code. Split into workspace
crates only when compile times or boundaries demand it; then the crate graph
becomes the layer rule.

**TypeScript SDK (library)**: `src/index.ts` is the public API (entry),
`src/<feature>/` are the feature folders, and `src/internal/` is core. Add a
public-API snapshot check (for example, API Extractor) so that breaking changes
become a check failure rather than something a reviewer has to notice. The
equivalents elsewhere are `cargo-semver-checks` for Rust and `griffe check` for
Python.
