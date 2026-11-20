from pathlib import Path

import yaml


def test_release_uses_the_artifact_from_the_clean_build():
    workflows = Path(__file__).resolve().parents[1] / "workflows"
    ci = yaml.safe_load((workflows / "ci.yml").read_text())["jobs"]
    release = yaml.safe_load((workflows / "release.yml").read_text())["jobs"]["release"]
    package = ci["package"]
    assert package["needs"] == "tests"
    assert all("pip install" not in step.get("run", "") for step in package["steps"])
    assert (
        len([step for step in ci["validate"]["steps"] if "upload-artifact" in step.get("uses", "")])
        == 0
    )
    downloader, publication = release["steps"]
    assert downloader["with"]["artifact-ids"] == "${{ needs.ci.outputs.archive_artifact_id }}"
    assert "sha256sum --check --strict SHA256SUMS" in publication["run"]
    assert '"${archives[@]}"' in publication["run"]
