# CI and review

## Contents

1. Why CI is part of the core
2. The CI workflow
3. Protecting the gates
4. The review layers
5. Generating the review skill
6. AI reviewer config
7. Make the review list shrink

## 1. Why CI is part of the core

Without CI, `check` only runs when an agent remembers to run it. A green CI run
is also what makes AI review worth paying for: a reviewer that has to point out
formatting diffs or layer violations is spending its budget on things `check`
catches in seconds. So set up CI before any reviewer config.

Rules:

- CI runs **the same `check` command agents run**, never a separate list of
  steps. If the two diverge, agents get green locally and red in CI, or the
  other way round.
- E2E runs in CI against the same local backend that local runs use, so it
  needs no secrets. Upload the failure artefacts.
- `check` (and e2e, where it exists) become **required statuses** on the
  default branch. A required check must have run once before it can be
  required, and rulesets are a repo-admin setting, so don't change them
  yourself: put the exact command (or settings path) in the final report, to
  run once the workflow has run on the default branch.

## 2. The CI workflow

**The path-filter trap**: when a workflow is skipped by `on: … paths:`, its
required checks stay "Pending" forever, which blocks every PR that doesn't touch
that path. When a *job* is skipped by an `if:` condition, it reports success. So
for a required check in a monorepo, filter paths at job level, not at workflow
level.

**Filter inputs**: include everything the app's checks depend on, not only its
folder. That means the root lockfile, the shared configs it extends, the
workspace packages it imports, and the workflow file itself. Otherwise a change
there skips the job, the job reports success, and the main branch breaks.

GitHub Actions shape, for an app at `<app>/` inside a larger repo. Adapt the
setup steps to the stack, and pin each action to its current major version
(shown here as `@vN`). `dorny/paths-filter` is a third-party action. If the org
blocks those, a `git diff --name-only` step against the base SHA does the same
job.

```yaml
name: <app>
on:
  pull_request:
  push:
    branches: [<default-branch>]

permissions:
  contents: read
  pull-requests: read

concurrency:
  group: <app>-${{ github.ref }}
  cancel-in-progress: true

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      app: ${{ steps.filter.outputs.app }}
    steps:
      - uses: actions/checkout@vN
      - uses: dorny/paths-filter@vN
        id: filter
        with:
          filters: |
            app:
              - '<app>/**'
              - '<root lockfile and shared configs>'
              - '<workspace packages the app imports>/**'
              - '.github/workflows/<this-file>.yml'

  <app>-check:
    needs: changes
    if: needs.changes.outputs.app == 'true'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <app>
    steps:
      - uses: actions/checkout@vN
      - <set up the runtime, with dependency caching>
      - run: <install from the lockfile, e.g. npm ci>
      - run: <check>

  <app>-e2e:
    needs: changes
    if: needs.changes.outputs.app == 'true'
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: <app>
    steps:
      - uses: actions/checkout@vN
      - <set up the runtime, with dependency caching>
      - run: <install>
      - run: <install browsers or services, e.g. npx playwright install --with-deps chromium>
      - run: <e2e>
      - uses: actions/upload-artifact@vN
        if: failure()
        with:
          name: <app>-e2e-artefacts
          path: <app>/<artefact dir>
```

Make `<app>-check` and `<app>-e2e` the required checks. Prefixing job names
with the app keeps two apps' `check` jobs from colliding in branch protection.

- **Single-app repo**: drop the `changes` job and the `if:` lines.
- **Optional extra steps**: `check-scaffold`, and a production build if routing
  or config changes often.
- **Other CI systems**: the same rules apply. Run the same command, scope it by
  path at job level, and make it required on the default branch.

Verify the workflow with `actionlint` if it's available. Nothing is pushed, so
its first real run happens when the user pushes the branch; say so in the
final report.

## 3. Protecting the gates

An agent under pressure to go green can weaken a gate rather than fix the code.
Some AI reviewers also read their instructions from the PR's own branch, so a
PR can edit the reviewer that's reviewing it. Two defences:

- **CODEOWNERS** on the gate files, with code-owner review required on the
  default branch. Add these entries only if a CODEOWNERS file already exists,
  using the owners it already names; otherwise list it as a follow-up in the
  final report. This is the one canonical list of gate files; other files point
  here:
  - the checker script and its config
  - CI workflows
  - lint, format and type configs, and the format-on-edit hooks
  - the test baseline, and any legacy suppression allowlist
  - AGENTS.md (its completeness block feeds every reviewer)
  - the review skill and bot configs
  - CODEOWNERS itself

  In a solo-maintainer repo, required code-owner review blocks the owner's own
  PRs. Don't change rulesets; list "add an owner bypass to the ruleset" as a
  follow-up.
- **The review skill flags gate changes** as needing justification, and treats
  a loosened gate as blocking.

## 4. The review layers

Each layer handles what the one before it can't:

| Layer                                  | Catches                                                                                       |
| -------------------------------------- | --------------------------------------------------------------------------------------------- |
| `check` in CI                          | everything mechanical: format, lint, types, boundaries, docs sync, suppression reasons, lost tests |
| The repo's review skill                | wrong behaviour, missing or weak tests, docs out of step with behaviour, shortcuts around the architecture |
| AI reviewer bots (Bugbot, Copilot, CodeRabbit, Claude in CI) | the same as the review skill, automatically on every PR, from synced copies of its checklist |
| Humans (and code owners)               | product judgement, gate changes, and whether the change should exist at all                    |

## 5. Generating the review skill

Start from `assets/review-skill-template.md`.

**Name**: `<repo>-review` (for example `acme-web-review`). Avoid a bare
`review`, which collides with built-in commands in some tools.

**Location**: wherever the repo already keeps skills. Otherwise use
`.claude/skills/<repo>-review/`, which the most tools read. Check the current
docs; common locations are:

| Tool                 | Reads project skills from                                                              |
| -------------------- | -------------------------------------------------------------------------------------- |
| Claude Code          | `.claude/skills/<name>/SKILL.md`                                                       |
| Cursor               | `.agents/skills/`, `.cursor/skills/`, and also `.claude/skills/` and `.codex/skills/`   |
| Codex                | `.agents/skills/`                                                                      |
| GitHub Copilot (including code review) | agent skills in the repo; check its docs for the directories          |

If the repo shows signs of a tool the chosen directory doesn't cover (for
example `.codex/` with the skill in `.claude/skills/`), keep one real copy and
add a symlink in that tool's directory. Skills usually live at the repo root,
even for one app inside a monorepo; in that case the skill's description names
the app path.

**Filling it in**: every `{{placeholder}}` is filled when you generate the
skill. Values only known at review time (the PR number, the changed paths) are
written as `<pr-number>` and `<paths>`, and they stay in the generated skill.

| Placeholder                                   | Source                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------- |
| `{{repo-slug}}`, `{{repo name}}`, `{{app-scope}}` | the repo; `{{app-scope}}` is " (the app under `<app>/`)" or empty      |
| `{{default-branch}}`                          | `git remote show origin` or `gh repo view --json defaultBranchRef`        |
| `{{check}}`, `{{e2e}}`, `{{owner}}`, `{{graph}}` | the literal invocations from 3.0, including the runner's argument separator where arguments follow (`npm run graph --`); drop the e2e lines if there's no e2e |
| `{{agents-md}}`, `{{feature map}}`, `{{worked example}}` | 3.6: paths to the AGENTS.md and FEATURE_MAP.md that apply (the nested ones for an app in a monorepo), and the worked example |
| `{{core}}`, `{{entry layer}}`                 | the chosen structure                                                     |
| `{{nested rules}}`                            | 3.6: each nested AGENTS.md, and what it covers                            |
| `{{skip markers}}`, `{{suppression syntax}}`  | `toolchains.md`, for the repo's languages                                 |
| `{{test levels}}`                             | the completeness checklist in AGENTS.md                                   |
| `{{baseline file}}`, `{{hotspots}}`           | 3.2; the audit                                                            |
| `{{domain edges}}`, `{{hazards}}`             | the audit: where bugs have clustered (`git log --grep=fix --name-only` per path), concurrency and realtime paths, auth, data migrations, money, time zones |
| `{{unenforced conventions}}`                  | repo conventions that no check enforces yet                               |
| The `completeness` sync block                 | paste it from AGENTS.md                                                   |

When you're done, grep the generated skill for `{{`; nothing should remain.
Keep it under ~150 lines. Leave the `sync` markers in place, because the bot
configs copy those blocks.

**Dry-run it** (Phase 4, step 11). Seed a small diff with one problem the checks
can't catch (a behaviour change without a FEATURE.md update) and one they can (a
formatting error). Ask for early feedback despite the red checks, since the
skill otherwise stops at red checks. It passes if the formatting error appears
only under "Checks" and the FEATURE.md gap appears as a finding. Then revert
the seeded diff.

If the team runs a dedicated review agent definition (for example, a subagent
file), keep it thin: it should say to use the `<repo>-review` skill, and
nothing more.

## 6. AI reviewer config

Configure the reviewer that's already set up, or the one picked in the plan's
question (nothing, if the answer was none). These products change
often, so confirm file names and fields in their current docs before writing
anything. If you can't reach the docs, use the shapes here and note it in the
final report. Keep each config short (a few thousand characters at most). It points
to the contract, and carries synced copies of two blocks:

- `review-hazards`, whose source is the review skill
- `completeness`, whose source is AGENTS.md

The copies are there because reviewers may not follow references, and some only
read the start of long instruction files.

**Cursor Bugbot**: `.cursor/BUGBOT.md`. The root file is always included. For
each changed file, Bugbot also includes every `.cursor/BUGBOT.md` it finds
walking up that file's directory tree. For an app inside a monorepo, add a
nested `<app>/.cursor/BUGBOT.md`, which applies only to changes under that
path.

```markdown
# Review rules for <app>

Read `<agents-md>`, `<feature map>` and the owning feature's FEATURE.md before reviewing.
`<check>` runs in CI. Don't report formatting, lint, import order or anything
else it enforces.

<!-- sync:review-hazards:start -->
…copied from the review skill…
<!-- sync:review-hazards:end -->

<!-- sync:completeness:start -->
…copied from AGENTS.md…
<!-- sync:completeness:end -->
```

**GitHub Copilot code review**: it reads `.github/copilot-instructions.md`, the
root `AGENTS.md`, path-specific `.github/instructions/**/*.instructions.md`
files, and agent skills, all from the PR's head branch. Add
`.github/instructions/<app>-review.instructions.md` with `applyTo:
"<app>/**"`, and the same body as above. Add `excludeAgent: "coding-agent"` if
the file should apply to review only.

**CodeRabbit**: `.coderabbit.yaml`, with the same body under
`reviews.path_instructions`:

```yaml
reviews:
  path_instructions:
    - path: "<app>/**"
      instructions: |
        Read <agents-md> and the owning FEATURE.md. Don't report what `<check>` enforces.
        <!-- sync:review-hazards:start -->
        …
        <!-- sync:review-hazards:end -->
        <!-- sync:completeness:start -->
        …
        <!-- sync:completeness:end -->
```

**Claude Code GitHub Action**: a review job running
`anthropics/claude-code-action` with `prompt: "/<repo>-review <pr-number>"`,
where `<pr-number>` is `${{ github.event.pull_request.number }}`.

- **Put it in the same workflow as `<app>-check`**, with
  `needs: [<app>-check]` and `if: github.event_name == 'pull_request'`, so it
  only reviews green PRs (the workflow also runs on pushes to the default
  branch, which have no PR to review). Give the workflow's `pull_request`
  trigger `types: [opened, synchronize, reopened, ready_for_review]`, and add
  `github.event.action != 'synchronize'` to the review job's `if:`, so it
  reviews when a PR opens or becomes ready, not on every push.
- **Run no PR code in this job.** It reads, and never runs `check`, tests or
  scripts from the PR, so its secrets are never exposed to code from a PR. The
  template's CI mode tells the skill to prove suspicions with reproduction
  steps rather than by running code.
- **Read the PR, but trust the base.** Check out the PR head with enough
  history to reach the base. Then restore the reviewer's instructions from the
  base branch, so a PR can't rewrite its own reviewer:
  `git checkout origin/<base> -- <skill dir> <agents-md> <bot configs>`.
- **Allow exactly the tools the skill needs** through `claude_args`
  (`--allowedTools`): read-only `gh pr` and `gh api` calls, read-only `git`
  commands, file reading and search, and the inline-comment tool if it posts
  comments.
- **Set job permissions as the action's docs say.** Its review example
  authenticates through the Claude GitHub App (`id-token: write`) with
  read-only repository permissions.

**Follow-ups for any reviewer**: installing its GitHub app, or adding the
secret the workflow uses, is a repo-admin step. List it in the final report
with the exact link or command.

**Others**: any reviewer that reads AGENTS.md already gets the contract. Give it
the two blocks through its own path-scoped instruction mechanism.

**Keeping the copies in sync**: the checker's `sync` rule compares each copy
with its source, and fails on any difference: "`<file>`: sync — block
`review-hazards` differs from its source `<skill path>`. Fix: copy it from
there."

## 7. Make the review list shrink

Every review finding that a script could have caught is a missing check.
When the same finding shows up twice, add a rule to the checker (or a lint
rule), remove the item from the checklist, and re-sync the copies. Over time,
`check` should grow and the review checklist should shrink, toward pure
judgement.
