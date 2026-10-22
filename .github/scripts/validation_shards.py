"""Partition the pinned validator's generated input list without editing upstream.

Run prepare/run from the vmecpp-validation checkout. The validator at 4017e53 has no
subset CLI, so run replaces only its input-list provider and scopes its structural
completeness check to that list. All solver, comparison and tolerance code stays
upstream. The aggregate check proves full coverage from manifests and the actual per-
configuration check summaries.
"""

import argparse
import importlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory


def config_names(confs):
    return [path.name.removeprefix("input.") for path in confs]


def make_manifest(confs, shard, count):
    names = config_names(confs)
    if not 0 <= shard < count or not names or len(set(names)) != len(names):
        message = "Invalid shard or empty/duplicate configuration list"
        raise ValueError(message)
    selected = names[shard::count]
    if not selected:
        message = "Empty validation shard"
        raise ValueError(message)
    return {"shard": shard, "count": count, "all": names, "selected": selected}


def prepare(shard, count):
    generation = importlib.import_module("src.input_generation")
    with TemporaryDirectory() as directory:
        confs = generation.make_input_configs(Path(directory), cache_dir=None)
        manifest = make_manifest(confs, shard, count)
    Path("manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    sys.stdout.write(
        f"Shard {shard}/{count}: {len(manifest['selected'])}/{len(confs)} configs\n"
    )


def run(shard, count):
    validator = importlib.import_module("validate_vmec")
    generate = validator.make_input_configs
    check_completeness = validator.check_all_checks_are_present
    manifest = json.loads(Path("manifest.json").read_text())

    def shard_configs(results_dir, cache_dir):
        confs = generate(results_dir, cache_dir)
        if make_manifest(confs, shard, count) != manifest:
            message = "Generated configurations differ from shard manifest"
            raise ValueError(message)
        return confs[shard::count]

    def check_shard(checks, reference_confs, _short):
        # short=True only selects the supplied names for this structural check.
        # main() still runs full mode, with all original numerical checks.
        check_completeness(checks, reference_confs, short=True)

    validator.__dict__["make_input_configs"] = shard_configs
    validator.__dict__["check_all_checks_are_present"] = check_shard
    sys.argv = ["validate_vmec.py"]
    return validator.main()


def check(root, count):
    expected = []
    assigned = []
    completed = []
    for shard in range(count):
        manifest = json.loads(
            (root / f"vnv-manifest-{shard}" / "manifest.json").read_text()
        )
        names = manifest["all"]
        if not expected:
            expected = names
        if (
            not names
            or len(set(names)) != len(names)
            or names != expected
            or manifest["shard"] != shard
            or manifest["count"] != count
            or manifest["selected"] != names[shard::count]
        ):
            message = f"Invalid manifest for shard {shard}"
            raise ValueError(message)
        summaries = list((root / f"vnv-summary-{shard}").rglob("all_vnv_checks.json"))
        if len(summaries) != 1:
            message = f"Expected one check summary for shard {shard}"
            raise ValueError(message)
        checks = json.loads(summaries[0].read_text())["checks"]
        if Counter(checks.keys()) != Counter(manifest["selected"]):
            message = f"Result coverage differs for shard {shard}"
            raise ValueError(message)
        if any(
            not entries or any(entry["status"] != "OK" for entry in entries)
            for entries in checks.values()
        ):
            message = f"Missing or failed checks in shard {shard}"
            raise ValueError(message)
        assigned.extend(manifest["selected"])
        completed.extend(checks)
        sys.stdout.write(f"Shard {shard}: {len(checks)} configurations validated\n")
    if Counter(assigned) != Counter(expected) or Counter(completed) != Counter(
        expected
    ):
        message = "Full validation has missing or duplicate configurations"
        raise ValueError(message)
    message = f"Validated {len(completed)}/{len(expected)} configurations exactly once."
    sys.stdout.write(message + "\n")
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as summary:
            summary.write(message + "\n")
    return message


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "run", "check"])
    parser.add_argument("shard_or_directory")
    parser.add_argument("count", type=int)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("count must be positive")
    if args.command == "check":
        check(Path(args.shard_or_directory), args.count)
        return 0
    # Match `python validate_vmec.py`: resolve validator imports from its checkout.
    sys.path.insert(0, str(Path.cwd()))
    shard = int(args.shard_or_directory)
    if args.command == "prepare":
        prepare(shard, args.count)
        return 0
    return run(shard, args.count)


if __name__ == "__main__":
    sys.exit(main())
