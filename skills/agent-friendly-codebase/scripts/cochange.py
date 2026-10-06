#!/usr/bin/env python3
"""Mine git history for hotspots, co-change and locality. Zero dependencies.

Run from the target repo:
  python3 <skill-dir>/scripts/cochange.py . [--since "6 months ago"]
      [--max-commits 300] [--max-files 40] [--depth 1] [--root src]
      [--top 20] [--ignore GLOB]... [--map candidate.json]...

Without --map: hotspot files, area co-change pairs, and current locality
(the share of commits that touched exactly one area). An area is a directory
at --depth below the repo root, or below --root. --root also limits the
analysis to files under that directory (for example, one app in a monorepo).

With --map: scores each candidate structure against today's layout on the
same basis. A map is JSON from feature names to globs, matched in order (first
match wins) against paths AS THEY APPEAR IN HISTORY (pre-move paths), relative
to --root if given:
  {"channels": ["components/channel-*", "lib/channels.ts"],
   "_entry": ["app/*"], "core": ["lib/*"]}
Groups whose names start with "_" (entry registrations, docs, config) are left
out of both scores. Files no glob matches keep their current area as their
bucket, so an incomplete map scores like today's layout for those files rather
than inflating the result. Globs use fnmatch: "*"
also matches "/", so "lib/*" covers everything under lib/.

Commits touching more than --max-files files (reformats, codemods, bumps) are
skipped and counted, so one sweeping commit can't dominate the results.
"""

import argparse
import collections
import fnmatch
import json
import signal
import subprocess
import sys

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

DEFAULT_IGNORE = [
    "*package-lock.json", "*pnpm-lock.yaml", "*yarn.lock", "*bun.lockb",
    "*Cargo.lock", "*poetry.lock", "*uv.lock", "*go.sum", "*Gemfile.lock",
    "*composer.lock", "*Package.resolved", "*mix.lock",
]


def git(repo, *args):
    out = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", repo, *args],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        sys.exit(f"git {args[0]} failed: {out.stderr.strip()}")
    return out.stdout


def commits(repo, since, max_commits):
    log = git(repo, "log", "--no-merges", f"--since={since}",
              f"--max-count={max_commits}", "--name-only", "--pretty=format:@@%h")
    result, current = [], None
    for line in log.splitlines():
        if line.startswith("@@"):
            current = [line[2:], []]
            result.append(current)
        elif line.strip() and current is not None:
            current[1].append(line.strip())
    return result


def area(path, depth):
    parts = path.split("/")
    if len(parts) == 1:
        return "(top-level files)"
    return "/".join(parts[:min(depth, len(parts) - 1)])


def bucket(path, mapping, depth):
    for name, globs in mapping.items():
        if any(fnmatch.fnmatch(path, g) for g in globs):
            return name
    return "(unmapped) " + area(path, depth)


def pct(n, d):
    return f"{(100 * n / d):.0f}%" if d else "n/a"


def score(sets):
    counted = [s for s in sets if s]
    single = sum(1 for s in counted if len(s) == 1)
    return single, len(counted)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--since", default="6 months ago")
    ap.add_argument("--max-commits", type=int, default=300)
    ap.add_argument("--max-files", type=int, default=40)
    ap.add_argument("--depth", type=int, default=1)
    ap.add_argument("--root", default="")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--ignore", action="append", default=[])
    ap.add_argument("--map", action="append", default=[])
    a = ap.parse_args()

    root = a.root.strip()
    while root.startswith("./"):
        root = root[2:]
    root = root.rstrip("/")
    if root == ".":
        root = ""
    if git(a.repo, "rev-parse", "--is-shallow-repository").strip() == "true":
        print("Warning: shallow clone; history is truncated. Run `git fetch --unshallow` "
              "for meaningful numbers.\n", file=sys.stderr)

    ignore = DEFAULT_IGNORE + a.ignore
    data, skipped = [], 0
    for sha, files in commits(a.repo, a.since, a.max_commits):
        kept = [f for f in files if not any(fnmatch.fnmatch(f, g) for g in ignore)]
        if root:
            kept = [f[len(root) + 1:] for f in kept if f.startswith(root + "/")]
        if not kept:
            continue
        if len(kept) > a.max_files:
            skipped += 1
            continue
        data.append((sha, kept))
    if not data:
        sys.exit("No commits with matching files in range. Try a wider --since, "
                 "or check --root.")

    where = f" under {root}/" if root else ""
    print(f"Analysed {len(data)} non-merge commits since {a.since!r}{where} "
          f"({skipped} skipped for touching more than {a.max_files} files).\n")

    file_counts = collections.Counter(f for _, fs in data for f in set(fs))
    print(f"Hotspots (files changed most often), top {a.top}:")
    for f, n in file_counts.most_common(a.top):
        print(f"  {n:4d}  {f}")

    area_sets = [{area(f, a.depth) for f in fs} for _, fs in data]
    area_counts = collections.Counter(x for s in area_sets for x in s)
    single, total = score(area_sets)
    print(f"\nCurrent locality (areas at depth {a.depth}{where}): {single}/{total} "
          f"commits ({pct(single, total)}) touched exactly one area.")
    top_area, top_n = area_counts.most_common(1)[0]
    deeper = any(area(f, a.depth) == top_area and area(f, a.depth + 1) != top_area
                 for _, fs in data for f in fs)
    if top_n > 0.6 * len(data) and len(area_counts) > 1 and deeper:
        print(f"  Hint: {top_area!r} appears in {pct(top_n, len(data))} of commits; "
              f"try --depth {a.depth + 1} to see inside it.")
    print("\nAreas by commits touching them:")
    for x, n in area_counts.most_common(a.top):
        print(f"  {n:4d}  {x}")

    pairs = collections.Counter()
    for s in area_sets:
        items = sorted(s)
        for i, x in enumerate(items):
            for y in items[i + 1:]:
                pairs[(x, y)] += 1
    print(f"\nAreas that change together (co-change pairs), top {a.top}:")
    for (x, y), n in pairs.most_common(a.top):
        print(f"  {n:4d}  {x}  +  {y}")

    for map_path in a.map:
        with open(map_path, encoding="utf-8") as fh:
            mapping = json.load(fh)
        today_sets, cand_sets = [], []
        per_feature = collections.Counter()
        unmapped = collections.Counter()
        multi = collections.Counter()
        for _, fs in data:
            today, cand = set(), set()
            for f in fs:
                b = bucket(f, mapping, a.depth)
                if b.startswith("_"):
                    continue
                today.add(area(f, a.depth))
                cand.add(b)
                if b.startswith("(unmapped)"):
                    unmapped[f] += 1
            today_sets.append(today)
            cand_sets.append(cand)
            for u in cand:
                per_feature[u] += 1
            if len(cand) > 1:
                multi[tuple(sorted(cand))] += 1
        t_single, t_total = score(today_sets)
        c_single, c_total = score(cand_sets)
        print(f"\n=== {map_path} ===")
        print(f"Same basis ('_' groups excluded, {c_total} commits):")
        print(f"  today's areas : {t_single}/{t_total} ({pct(t_single, t_total)}) "
              f"touched exactly one area")
        print(f"  this candidate: {c_single}/{c_total} ({pct(c_single, c_total)}) "
              f"touched exactly one feature")
        print("Commits per feature:")
        for u, n in per_feature.most_common():
            print(f"  {n:4d}  {u}")
        if multi:
            print(f"Most common multi-feature combinations, top {a.top}:")
            for combo, n in multi.most_common(a.top):
                print(f"  {n:4d}  {' + '.join(combo)}")
        if unmapped:
            print(f"Unmapped files ({len(unmapped)}), scored by their current area; "
                  f"assign them to a feature or a '_' group. Top {a.top}:")
            for f, n in unmapped.most_common(a.top):
                print(f"  {n:4d}  {f}")


if __name__ == "__main__":
    main()
