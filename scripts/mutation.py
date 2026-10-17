"""Run scoped mutations and summarize their results using mutmut's CLI."""

import argparse
import subprocess
import sys
from collections import Counter
from fnmatch import fnmatchcase
from pathlib import Path


def print_results(output: str, scope: str) -> None:
    """Print counts and review candidates for the selected mutation scope."""
    results = []
    for line in output.splitlines():
        name, separator, status = line.strip().partition(": ")
        if separator and fnmatchcase(name, scope):
            results.append((name, status))
    if not results:
        raise ValueError(f"No mutation results matched {scope!r}.")

    counts = Counter(status for _, status in results)
    print(f"\nSelected mutations: {len(results)}")
    print(f"Killed (tests detected the change): {counts.pop('killed', 0)}")
    print(f"Survived (tests did not detect the change): {counts.pop('survived', 0)}")
    for status, count in sorted(counts.items()):
        print(f"{status}: {count}")

    review = [
        (name, status)
        for name, status in results
        if status not in {"killed", "caught by type check", "skipped"}
    ]
    if review:
        print("\nReview candidates (survivors can be behaviorally equivalent):")
        for name, status in review:
            print(f"  {status}: {name}")
        print(f"\nInspect a change: {sys.executable} -m mutmut show {review[0][0]}")


def main(scope: str) -> int:
    """Rerun the selected scope and retain raw output for troubleshooting."""
    log_path = Path("mutants/mutation.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Rerunning mutations matching: {scope}", flush=True)
    print(f"Raw output: {log_path} (overwritten each run)", flush=True)
    command = [sys.executable, "-m", "mutmut"]
    with log_path.open("w", encoding="utf-8") as log:
        run = subprocess.run(
            [*command, "run", scope], stdout=log, stderr=subprocess.STDOUT, check=False
        )
        if run.returncode:
            print(f"Mutation run failed (exit {run.returncode}); see {log_path}.")
            return run.returncode

        report = subprocess.run(
            [*command, "results", "--all", "true"],
            capture_output=True,
            text=True,
            check=False,
        )
        if report.returncode:
            log.write(report.stdout + report.stderr)
            print(f"Could not read mutation results; see {log_path}.")
            return report.returncode

    try:
        print_results(report.stdout, scope)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", help="Mutmut name or wildcard pattern to rerun")
    raise SystemExit(main(parser.parse_args().scope))
