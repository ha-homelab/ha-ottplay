"""Verify the two install layouts contain only reproducible tracked inputs."""

import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import pytest


def builder():
    path = Path(__file__).parents[1] / "scripts/package_release.py"
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("ottplay_package", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture_repo(tmp_path):
    root = tmp_path / "repo"
    component = root / "custom_components/ottplay"
    component.mkdir(parents=True)
    (component / "manifest.json").write_text(
        json.dumps({"domain": "ottplay", "name": "OTTPlay", "version": "0.1.0b1"})
    )
    (component / "__init__.py").write_text('"""OTTPlay."""\n')
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    (component / "local-secret.json").write_text("DO NOT PACKAGE")
    return root


def test_reproducible_exact_install_layouts(tmp_path):
    module = builder()
    root = fixture_repo(tmp_path)
    with patch.object(module, "checked_version"):
        first = module.build(root, "0.1.0", "beta", tmp_path / "first")
        second = module.build(root, "0.1.0", "beta", tmp_path / "second")
    assert len(first) == 2
    for a, b in zip(first, second, strict=True):
        assert a.read_bytes() == b.read_bytes()
        with ZipFile(a) as archive:
            prefix = "custom_components/ottplay/" if a.name == "ha-ottplay.zip" else ""
            assert set(archive.namelist()) == {prefix + "__init__.py", prefix + "manifest.json"}
            assert json.loads(archive.read(prefix + "manifest.json"))["version"] == "0.1.0b1"
        assert (
            f"{hashlib.sha256(a.read_bytes()).hexdigest()}  {a.name}"
            in (a.parent / "SHA256SUMS").read_text()
        )


def test_refuse_overwrite_and_symlink(tmp_path):
    module = builder()
    root = fixture_repo(tmp_path)
    output = tmp_path / "output"
    output.mkdir()
    (output / "keep").write_text("keep")
    with patch.object(module, "checked_version"), pytest.raises(ValueError, match="empty"):
        module.build(root, "0.1.0", "beta", output)
    component = root / "custom_components/ottplay"
    (component / "__init__.py").unlink()
    (component / "__init__.py").symlink_to(component / "local-secret.json")
    with patch.object(module, "checked_version"), pytest.raises(ValueError, match="regular"):
        module.build(root, "0.1.0", "beta", tmp_path / "new")


@pytest.mark.parametrize("suffix", ["-beta.1", "-rc.1", ""])
def test_current_changelog_passes_real_release_parser(suffix, monkeypatch):
    """Fail CI before publishing when this repository's notes violate the contract."""
    root = Path(__file__).parents[1]
    monkeypatch.syspath_prepend(str(root / "scripts"))
    import release_control

    source_sha = "a" * 40
    policy = json.loads((root / ".release-policy.json").read_text())
    requests = []

    class RepositorySource:
        repo = policy["repository"]

        def api(self, path):
            requests.append(path)
            files = {
                f"contents/{name}?ref={source_sha}": name
                for name in (".release-policy.json", "CHANGELOG.md")
            }
            name = files[path]
            raw = (root / name).read_bytes()
            return {
                "type": "file",
                "path": name,
                "encoding": "base64",
                "content": base64.b64encode(raw).decode(),
                "size": len(raw),
                "sha": hashlib.sha1(
                    b"blob " + str(len(raw)).encode() + b"\0" + raw,
                    usedforsecurity=False,
                ).hexdigest(),
            }

    version = (root / "version").read_text().strip()
    body = release_control.release_notes(
        RepositorySource(), f"v{version}{suffix}", source_sha, "Verified build provenance."
    )
    assert f"Changes in {version}" in body
    assert "### Upgrade" in body and "### Security" in body
    assert body.endswith("Verified build provenance.")
    assert requests == [
        f"contents/.release-policy.json?ref={source_sha}",
        f"contents/CHANGELOG.md?ref={source_sha}",
    ]
