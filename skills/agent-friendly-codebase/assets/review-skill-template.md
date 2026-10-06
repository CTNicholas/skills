---
name: "{{repo-slug}}-review"
description: >-
  Review a diff, branch, commit or pull request in {{repo name}}{{app-scope}}
  against its agent contract. Confirms the checks are green, reads the
  contract and the owning {{unit doc}} for every touched {{unit}}, then
  reports only what the checks cannot catch: real bugs, behaviour changed
  without docs or tests, weakened or deleted tests, architecture shortcuts,
  loosened gates and contract drift. Use whenever asked to review, check, look
  over or approve changes in this repo, and for self-review before declaring
  work done.
---

# Reviewing changes in {{repo name}}

Your job is to find what `{{check}}` can't: wrong behaviour, missing tests or
docs, and shortcuts around the architecture. Formatting, lint, layer rules,
docs sync, suppression reasons and test counts are already enforced, so don't
spend findings on them.

## 1. Get the change

- Pull request: `gh pr view <pr-number> --json title,body,baseRefName,files,comments`
  and `gh pr diff <pr-number>`
- Branch: `git fetch origin {{default-branch}}`, then
  `git diff origin/{{default-branch}}...HEAD` and
  `git log --oneline origin/{{default-branch}}..HEAD`
- Working tree: `git diff HEAD` and `git status --porcelain` (to see new files)

Read the PR description: what does it claim to do? You'll check that claim. Map
the touched files to units with `{{owner}} <paths>`.

If the PR already has review comments, don't repeat findings that were already
raised. Inline comments aren't in `gh pr view`; fetch them with
`gh api repos/{owner}/{repo}/pulls/<pr-number>/comments --paginate`.

**In CI**, run no code from the PR: no `{{check}}`, no tests, no scripts. Read
only, and prove suspicions with exact reproduction steps instead of a failing
test.

## 2. Gate on the checks

- Locally: run `{{check}}`, plus `{{e2e}}` if a user flow changed.
- On a PR: `gh pr checks <pr-number>`. In CI, this review runs as a job that
  depends on the check job, so the gate is already satisfied. Ignore your own
  pending job.
- If the checks are red, report the failing command and its first errors under
  "Checks", then stop; re-review once they're green. If you were asked for
  early feedback anyway, carry on, and say the checks are red.
- If you can't run the checks, say so under "Not verified".

## 3. Load the contract

- `{{agents-md}}`
- `{{feature map}}`, especially the shared code tables, to spot new helpers
  that duplicate existing ones
- The {{unit doc}} of every touched {{unit}}, and of every unit whose public
  surface it changed (`{{graph}} <unit> --reverse` lists them)
- Scoped rules for the touched paths: {{scoped rules}}
- `{{worked example}}`, for what a complete change looks like

## 4. Review

Read changed code in context: open the whole function and its callers, not
just the hunk.

### Correctness (most of the value is here)

- Trace one realistic input through each new or changed branch. Then try the
  edges: empty, missing, duplicate, very large, concurrent, retried, offline,
  unauthorised.
- Error paths: is every failure handled or deliberately propagated? Is anything
  swallowed?
- Does the change do what the PR says, and nothing else? Unrelated behaviour
  changes are findings.
- Security: authorisation on new endpoints and handlers, input validation at
  trust boundaries, secrets in code, logs or client bundles, injection.
- Data: schema and migration changes are compatible with the running code and
  reversible.

When you suspect a bug, try to prove it: locally with a failing test (don't
commit it), in CI with exact reproduction steps. Label each finding *confirmed*
or *suspected*.

<!-- sync:review-hazards:start -->
### Hazards specific to this repo

- {{hazards}}
- Edge cases that matter here: {{domain edges}}

### Architecture and contract

- No new dependency between units where the shared piece belongs in
  `{{core}}`. No logic in `{{entry layer}}`.
- No new helper that duplicates one in the shared code tables of
  `{{feature map}}`.
- A new name for a unit that users will see (UI copy, a route, a command) is
  added to that unit's "Also called" in `{{feature map}}`.
- {{unit doc}} edits describe behaviour. They don't add counts or constants
  copied from code; the only file list is the checker-verified `## Files`.
- Hotspot files ({{hotspots}}) are touched only when there's no local
  alternative.
- No tests skipped ({{skip markers}}) or weakened, and `{{baseline file}}` isn't
  lowered, unless the PR says why.
- New suppressions ({{suppression syntax}}) have reasons that hold up.
- Changes to the gates (checker and its config, lint, format or type config,
  baseline, CI, CODEOWNERS, this skill, bot configs) are called out and
  justified. A gate loosened to get to green is blocking.
- {{unenforced conventions}}

### Ignore

Formatting, import order, naming the linter covers, anything `{{check}}`
enforces, generated files, lockfiles, vendored code, snapshot churn, style
preferences that aren't in the contract, and refactors outside the diff
(unless the diff makes something worse).
<!-- sync:review-hazards:end -->

### Completeness

Test levels for this repo: {{test levels}}.

<!-- sync:completeness:start -->
{{paste the completeness block from AGENTS.md}}
<!-- sync:completeness:end -->

## 5. Report

**Blocking** means one of:

- a confirmed bug
- a security issue (confirmed or suspected)
- possible data loss
- a loosened gate
- new or changed behaviour with no test

Everything else is **Should fix** (at most three items; drop the weakest) or
not worth mentioning. A suspected finding is never Blocking unless it's a
security issue.

```
Verdict: approve | request changes | discuss
Checks: <what ran, result>   Read: <docs read>

Blocking
1. path/to/file:42 — <what's wrong>. <Concrete failure: input → wrong result>. Fix: <specific change>. (confirmed | suspected)

Should fix
1. …

Contract drift
- <doc or rule now out of step with the code, and the edit that fixes it>

Not verified
- <what you couldn't run or check, and the command that would>
```

- Every finding names the file and line, a concrete failure, and a fix. No
  praise, and no restating the diff.
- If you find nothing, write "Verdict: approve" and list what you checked.
  Don't invent findings to look thorough.
- When running in CI with a comment tool available, post each finding as an
  inline comment on its line, and the verdict as one summary comment.

## 6. Make this list shrink

If a finding is mechanical (a script could have caught it), note it under
"Contract drift" and propose the check that would catch it. Every recurring
finding should eventually move into `{{check}}`.
