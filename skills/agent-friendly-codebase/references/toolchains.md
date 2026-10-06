# Toolchains: commands per ecosystem

Use the repo's existing tools first. Only introduce a tool when the role is
empty, and say so in the report. Tool versions and flags change, so confirm
each command against the installed version (`--help`) before relying on it.

## Contents

- Task runners and the `check` entry point
- Skip markers, suppressions and magic comments
- JavaScript / TypeScript
- Python
- Go
- Rust
- JVM (Java / Kotlin, including Android)
- .NET
- Ruby / Rails
- Elixir / Phoenix
- PHP
- Swift
- Monorepos and polyglot repos
- Ecosystems not listed here
- Writing repo scripts

## Task runners and the `check` entry point

Agents discover commands where the ecosystem keeps them, so put `check` there:

| Ecosystem | Where `check` lives                                                                                                    |
| --------- | ---------------------------------------------------------------------------------------------------------------------- |
| JS/TS     | `package.json` scripts (use the package manager the lockfile shows: npm, pnpm, yarn or bun)                             |
| Python    | whatever exists (Makefile, justfile, poethepoet under `uv run`, nox, tox, hatch scripts); if nothing exists, a justfile or Makefile |
| Go        | Makefile, Taskfile or mage                                                                                             |
| Rust      | cargo aliases in `.cargo/config.toml`, `cargo xtask`, or a justfile                                                    |
| JVM       | hook into Gradle's `check` task (or the Maven `verify` lifecycle), which is already the convention                     |
| Others    | a Makefile or justfile at the root                                                                                     |

Role names in SKILL.md (`check`, `check-unit`, `fix`, `structure`…) are
abstract. Name them the way the runner expects, and always document the
literal invocation in AGENTS.md:

| Runner          | Naming                                                    | Scoped invocation (`check-unit`)                        |
| --------------- | --------------------------------------------------------- | ------------------------------------------------------- |
| npm/pnpm/yarn/bun | `check`, `check:unit`, `lint:structure`, `new:feature` (colons by convention) | `npm run check:unit -- <unit>`         |
| just            | `check`, `check-unit` (recipe names can't contain colons) | `just check-unit <unit>`                                |
| make            | `check`, `check-unit`                                     | `make check-unit UNIT=<unit>` (`make check <path>` would parse the path as a target) |
| Gradle          | the built-in `check` task per module                      | `./gradlew :<module>:check`                             |
| cargo xtask     | `cargo xtask check`                                       | `cargo xtask check <crate>`                             |
| poethepoet / nox | `check`, `check-unit`                                    | `uv run poe check-unit <unit>`, `nox -s check -- <unit>` |

In npm, a chained script (`"check": "a && b"`) passes `-- <arg>` only to its
last command. So `check-unit` must be a small script that parses its argument
and runs each step itself. See `checks-and-scripts.md`.

## Skip markers, suppressions and magic comments

The `suppressions` and `comments` rules and the review skill need this syntax
for the repo's languages. Three kinds of thing, treated differently:

- **Suppressions** switch a check off for a line. Each one needs an inline
  reason, and the `suppressions` rule enforces that. A reason written as a
  trailing comment on the same line is allowed under any comments policy.
- **Type escapes** are ordinary language features that bypass the type system.
  Don't demand a reason for each one. Ban the risky ones with a lint rule where
  one exists (for example `@typescript-eslint/no-explicit-any`); otherwise
  leave them to the review skill.
- **Magic comments** are comments the toolchain reads. They're always allowed
  under any comments policy.

| Ecosystem | Skip / focus markers                                        | Suppressions (need a reason)                                   | Type escapes (lint rule or review)          | Magic comments (always allowed)                       |
| --------- | ----------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------- |
| JS/TS     | `.skip`, `.only`, `.todo`, `xit`, `xdescribe`, `test.fixme` | `eslint-disable…` (reason after `--`), `@ts-expect-error`, `@ts-ignore`, `biome-ignore` | `as any`, `as unknown as`, non-null `!`     | shebang, `/// <reference>`, test-environment pragmas   |
| Python    | `@pytest.mark.skip`, `skipif`, `xfail`, `pytest.skip()`     | `# type: ignore[code]`, `# noqa: CODE`, `# pyright: ignore`, `# pragma: no cover` | `cast(…)`, `Any`                            | shebang, encoding line                                 |
| Go        | `t.Skip(…)`                                                 | `//nolint:<linter> // reason` (nolintlint can require it)       | `unsafe`, unchecked type assertions         | `//go:build`, `//go:generate`, `//go:embed`, cgo preamble |
| Rust      | `#[ignore]`                                                 | `#[allow(…)]` / `#[expect(…, reason = "…")]`                    | `unsafe` blocks (keep `// SAFETY:` notes)   | (attributes, not comments)                             |
| JVM       | `@Disabled`, `@Ignore`, `assumeTrue`                        | `@SuppressWarnings`, `@Suppress`, `//noinspection`, `// NOPMD`, `// CHECKSTYLE:OFF` | unchecked casts, `!!` (Kotlin)              | —                                                      |
| .NET      | `[Fact(Skip = "…")]`, `[Ignore]`                            | `#pragma warning disable`, `[SuppressMessage]`                  | `!` (null-forgiving), `dynamic`             | (directives, not comments)                             |
| Ruby      | `skip`, `xit`, `pending`                                    | `# rubocop:disable`                                             | `T.unsafe`, `T.must`                        | `# frozen_string_literal: true`, `# typed:` (Sorbet), shebang |
| Elixir    | `@tag :skip`                                                | `# credo:disable-for-next-line`, `@dialyzer`                    | —                                           | —                                                      |
| PHP       | `markTestSkipped`, `->skip()`                               | `@phpstan-ignore`, `@psalm-suppress`, `// phpcs:ignore`         | `@var` overrides                            | —                                                      |
| Swift     | `XCTSkip`, `.disabled` (Swift Testing)                      | `// swiftlint:disable`                                          | `!` force unwrap, `as!`                     | `// swift-tools-version:` (required in Package.swift), `// MARK:` |

If a language isn't listed, find its required magic comments before turning on
a "no comments" policy.

## JavaScript / TypeScript

| Role             | Tooling                                                                                                                                         |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Format           | Prettier (`prettier --check .` / `--write`), or Biome (`biome format`, `biome check`)                                                            |
| Lint             | ESLint flat config with the framework preset and `--max-warnings 0`, or Biome lint with `--error-on-warnings`                                    |
| Typecheck        | `tsc --noEmit` (`tsc -b` with project references); Vue: `vue-tsc --noEmit`; Svelte: `svelte-check`                                               |
| Unit tests       | Vitest or Jest                                                                                                                                  |
| Test counts      | Vitest `--reporter=json --outputFile=f.json`, or Jest `--json --outputFile=f.json`: files = `testResults.length`, tests = `numTotalTests` (in Vitest, `numTotalTestSuites` counts describe blocks, so don't use it for files) |
| E2E              | Playwright. `playwright test --list` ends with "Total: N tests in M files" and needs no browser. For Cypress, count spec files.                  |
| Scoped           | `vitest run <path>`, `eslint <path>`, `prettier --check <path>`, `playwright test <path>`                                                       |
| Boundaries       | a zero-dependency `.mjs` script; or dependency-cruiser, eslint-plugin-boundaries, or Nx `enforce-module-boundaries` in Nx workspaces           |
| Public surface   | an `index.ts` barrel with named exports only                                                                                                    |
| Coverage         | `vitest run --coverage` (v8 provider), or `jest --coverage`                                                                                     |
| Comment detection | A line-based detector must ignore `//` and `/*` inside string, template and regex literals. If it can't, document that a regex containing `/*` must be written `\/\*`. |

Point each runner's globs at its own suffix only. For example, unit tests at
`**/tests/*.test.{ts,tsx}` and e2e at `**/tests/*.spec.ts`.

## Python

| Role            | Tooling                                                                                                    |
| --------------- | ---------------------------------------------------------------------------------------------------------- |
| Format          | `ruff format --check` (or `black --check`)                                                                 |
| Lint            | `ruff check` (any finding fails)                                                                           |
| Typecheck       | mypy or pyright. Turn on strictness only if the code is already close to passing it.                        |
| Tests           | pytest                                                                                                     |
| Test counts     | `pytest --collect-only -q`: the last line gives "N tests collected"; files = unique node-id prefixes before `::` |
| Scoped          | `pytest <path>`, `ruff check <path>`, `ruff format --check <path>`, `mypy <path>`                          |
| Boundaries      | import-linter (layers, independence and forbidden contracts) or tach; plus a stdlib `ast` script for repo rules |
| Public surface  | the package's `__init__.py` with an explicit `__all__`; no `from x import *`                               |
| Coverage        | `pytest --cov=<pkg>` (pytest-cov)                                                                          |

## Go

| Role            | Tooling                                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------------------- |
| Format          | `test -z "$(gofmt -l .)"` (gofmt has no check mode, so fail on any output); goimports if it's already in use      |
| Lint            | `golangci-lint run` (depguard handles import rules), `go vet ./...`                                              |
| Typecheck       | `go build ./...`                                                                                                 |
| Tests           | `go test ./...`                                                                                                  |
| Test counts     | `go test -list '.*' ./...` (count lines that start with `Test`, `Example` or `Fuzz`); files = number of `_test.go` files |
| Scoped          | `go test ./internal/<unit>/...`, `golangci-lint run ./internal/<unit>/...`                                        |
| Boundaries      | the compiler forbids import cycles and `internal/` restricts visibility; depguard or go-arch-lint enforce layer direction; `go list -json ./...` gives the import graph for repo scripts |
| Public surface  | exported identifiers of the unit package; keep internals in a sub-`internal/` package                            |
| Doc comments    | Exported doc comments are a Go convention; keep them under a "public API docs only" policy. |

## Rust

| Role            | Tooling                                                                                                                 |
| --------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Format          | `cargo fmt --all --check`                                                                                               |
| Lint            | `cargo clippy --all-targets -- -D warnings` (add `--all-features` only if the features are additive)                     |
| Tests           | `cargo test`                                                                                                            |
| Test counts     | `cargo test -- --list` (count lines ending in `: test`)                                                                 |
| Scoped          | `cargo test -p <crate>`, `cargo clippy -p <crate>`                                                                      |
| Boundaries      | workspace crates (the Cargo dependency graph is the layer rule, and cycles are impossible); `pub(crate)` visibility; `cargo metadata --format-version 1` for repo scripts |
| Public API      | `cargo-semver-checks` for libraries                                                                                     |
| Unsafe          | Keep `// SAFETY:` comments on `unsafe` blocks; clippy's `undocumented_unsafe_blocks` lint (off by default) can require them. |

## JVM (Java / Kotlin, including Android)

| Role        | Tooling                                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| Format      | Spotless (google-java-format, ktfmt or ktlint)                                                                       |
| Lint        | Error Prone, Checkstyle, PMD or detekt, with warnings as errors; Android Lint with `warningsAsErrors`                  |
| Tests       | JUnit 5. On Android: `src/test` for local tests, `src/androidTest` for instrumented tests                            |
| Test counts | sum the `tests` attributes in the JUnit XML reports (`build/test-results/**/*.xml` or `target/surefire-reports`)     |
| Boundaries  | one Gradle/Maven module per unit (on Android, `:feature:<name>` and `:core:<name>`); ArchUnit tests for layer rules; Spring Modulith's `ApplicationModules.of(App.class).verify()` for Spring Boot |

## .NET

| Role        | Tooling                                                                                       |
| ----------- | --------------------------------------------------------------------------------------------- |
| Format      | `dotnet format --verify-no-changes`                                                           |
| Lint        | Roslyn analyzers with `TreatWarningsAsErrors`                                                 |
| Tests       | `dotnet test`; counts from `dotnet test --list-tests`                                         |
| Boundaries  | one project per unit (project references are the layer rules); NetArchTest or ArchUnitNET     |

## Ruby / Rails

| Role        | Tooling                                                                                      |
| ----------- | -------------------------------------------------------------------------------------------- |
| Format/lint | rubocop (rubocop-rails); Sorbet or Steep if typing is already in use                         |
| Tests       | RSpec (counts from `rspec --dry-run --format json`, field `summary.example_count`) or minitest |
| Boundaries  | packwerk (`packs/<unit>/package.yml` declares dependencies) or Rails engines                 |

## Elixir / Phoenix

| Role        | Tooling                                                                    |
| ----------- | -------------------------------------------------------------------------- |
| Format/lint | `mix format --check-formatted`, `mix credo --strict`, dialyzer             |
| Tests       | `mix test`                                                                 |
| Boundaries  | Phoenix contexts are the units; the `boundary` library enforces them at compile time |

## PHP

| Role        | Tooling                                                      |
| ----------- | ------------------------------------------------------------ |
| Format/lint | PHP-CS-Fixer or PHP_CodeSniffer; PHPStan or Psalm             |
| Tests       | PHPUnit or Pest (`phpunit --list-tests` for counts)          |
| Boundaries  | deptrac                                                      |

## Swift

| Role        | Tooling                                                                         |
| ----------- | ------------------------------------------------------------------------------- |
| Format/lint | swift-format or SwiftFormat; SwiftLint `--strict`                               |
| Tests       | `swift test` (counts from `swift test list`; older toolchains use `--list-tests`) |
| Boundaries  | SwiftPM targets per unit (target dependencies are the layer rules); for Xcode apps, local packages |

## Monorepos and polyglot repos

- Root `check` delegates to each package (turbo, nx, `pnpm -r`, moon, Bazel,
  just or make) and runs only what's affected in CI: `turbo run check
  --affected`, `nx affected -t check`, or a path filter per package.
- Each package has its own `check`, so an agent working in one package never
  needs to run the whole repo.
- The package dependency graph is the layer rule. Declare every dependency
  explicitly (strict workspace resolution, or Nx tags).
- If an app inside the monorepo is excluded from root CI, say so in the report,
  and let the user decide whether to add a scoped workflow.

## Ecosystems not listed here

For Dart/Flutter, C/C++ (CMake), Scala, Haskell and others, fill the same roles
with the ecosystem's standard tools: formatter, linter with warnings as errors,
compiler or typechecker, test runner with a list or machine-readable mode, and
a boundary mechanism (packages, modules or build targets). Say in the report
which roles you couldn't fill, and why.

## Writing repo scripts

- Write them in the repo's primary language, using only its standard library:
  Node `.mjs` for JS/TS, Python stdlib for Python, `go run ./tools/<x>` for Go,
  `cargo xtask` for Rust. They then never break when a dependency is bumped.
- On the JVM and .NET, express boundary rules as tests (ArchUnit, NetArchTest)
  so they run inside the normal test task.
- Use machine-readable sources instead of parsing source text where they
  exist: `go list -json`, `cargo metadata`, test-runner JSON reports,
  `--list` modes.
- For comment detection, use the language's own tokenizer where it ships one:
  Python's `tokenize`, Go's `go/scanner`, or TypeScript's scanner when
  `typescript` is already a dependency. Otherwise use a line-based detector
  that ignores string, template and regex literals.
