"""Coverage and failure propagation checks using synthetic configurations."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import validation_shards as shards


@pytest.fixture
def coverage(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    confs = [Path(f"input.synthetic_{index}") for index in range(11)]
    for shard in range(3):
        manifest = shards.make_manifest(confs, shard, 3)
        directory = Path(f"vnv-manifest-{shard}")
        directory.mkdir()
        (directory / "manifest.json").write_text(json.dumps(manifest))
        directory = Path(f"vnv-summary-{shard}")
        directory.mkdir()
        checks = {name: [{"status": "OK"}] for name in manifest["selected"]}
        (directory / "all_vnv_checks.json").write_text(json.dumps({"checks": checks}))
    return confs


@pytest.mark.usefixtures("coverage")
def test_aggregate_counts_every_configuration():
    assert "11/11" in shards.check(Path.cwd(), 3)


@pytest.mark.usefixtures("coverage")
@pytest.mark.parametrize(
    "defect", ["missing", "extra", "empty", "mismatch", "no-summary"]
)
def test_aggregate_rejects_incomplete_or_failed_validation(defect):
    path = Path("vnv-summary-1/all_vnv_checks.json")
    summary = json.loads(path.read_text())
    checks = summary["checks"]
    name = next(iter(checks))
    if defect == "missing":
        del checks[name]
    elif defect == "extra":
        checks["unexpected"] = [{"status": "OK"}]
    elif defect == "empty":
        checks[name] = []
    else:
        checks[name][0]["status"] = "MISMATCH"
    path.write_text(json.dumps(summary))
    if defect == "no-summary":
        path.unlink()
    with pytest.raises(ValueError, match="shard 1"):
        shards.check(Path.cwd(), 3)


@pytest.mark.usefixtures("coverage")
def test_duplicate_assignment_fails():
    path = Path("vnv-manifest-1/manifest.json")
    manifest = json.loads(path.read_text())
    manifest["selected"][0] = "synthetic_0"
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Invalid manifest for shard 1"):
        shards.check(Path.cwd(), 3)


def test_runner_uses_full_generator_and_propagates_failure(coverage):
    manifest = shards.make_manifest(coverage, 1, 3)
    Path("manifest.json").write_text(json.dumps(manifest))
    checked = []
    validator = SimpleNamespace(
        make_input_configs=lambda _directory, _cache: coverage,
        check_all_checks_are_present=lambda _checks, confs, short: checked.append(
            (confs, short)
        ),
    )

    def main():
        assert sys.argv == ["validate_vmec.py"]
        confs = validator.make_input_configs(Path.cwd(), None)
        assert confs == coverage[1::3]
        validator.check_all_checks_are_present({}, confs, False)
        return 7

    validator.main = main
    with (
        patch.object(shards.importlib, "import_module", return_value=validator),
        patch.object(sys, "argv", ["wrapper"]),
    ):
        assert shards.run(1, 3) == 7
    assert checked == [(coverage[1::3], True)]
