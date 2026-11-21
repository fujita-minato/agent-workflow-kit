#!/usr/bin/env python3
"""Exercise release checks and both local installation paths."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_delivery import check
from install import install
from privacy_check import scan


class WorkflowTest(unittest.TestCase):
    def test_roles_and_installed_skills(self):
        with TemporaryDirectory() as folder:
            target = Path(folder)
            self.assertGreater(install(target, "both"), 0)
            self.assertEqual(install(target, "both"), 0)
            claude = target / ".claude"
            codex = target / ".codex"
            role_names = {path.stem for path in (claude / "agents").glob("*.md")}
            self.assertEqual(len(role_names), 7)
            self.assertEqual(role_names, {path.stem for path in (codex / "agents").glob("*.toml")})
            for path in (codex / "agents").glob("*.toml"):
                parsed = tomllib.loads(path.read_text())
                self.assertEqual(parsed["name"], path.stem)
                self.assertTrue(parsed["description"])
                self.assertTrue(parsed["developer_instructions"])
            for base in (claude / "skills", target / ".agents" / "skills"):
                skills = list(base.glob("*/SKILL.md"))
                self.assertEqual(len(skills), 7)
                for path in skills:
                    self.assertIn(f"\nname: {path.parent.name}\ndescription:", path.read_text())
                self.assertTrue((base / "deliver-revision/references/review-record.md").is_file())

            result = subprocess.run([
                sys.executable, "-B", str(target / ".agent-workflow-local/check_delivery.py"),
                str(ROOT / "examples/desk-lamp/review.json"),
            ], check=True, capture_output=True, text=True)
            self.assertIn("PASS: final.md", result.stdout)

    def test_install_conflict_and_symlink(self):
        with TemporaryDirectory() as folder:
            target = Path(folder)
            agent = target / ".claude/agents/independent-reviewer.md"
            agent.parent.mkdir(parents=True)
            agent.write_text("existing project role")
            with self.assertRaisesRegex(ValueError, "Existing file differs"):
                install(target, "both")
            self.assertEqual(agent.read_text(), "existing project role")
            self.assertFalse((target / ".codex").exists())
            (target / ".agents").symlink_to(target / ".claude", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "Conflicting path"):
                install(target, "codex")

    def test_film_requires_both_reviews_of_exact_version(self):
        with TemporaryDirectory() as folder:
            bundle = Path(folder)
            artifact = bundle / "test.mp4"
            artifact.write_bytes(b"fictional test bytes")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            record = bundle / "review.json"
            content = bundle / "content.md"
            visual = bundle / "visual.md"
            content.write_text("Fictional evidence for content")
            visual.write_text("Separate fictional visual evidence")
            details = {
                "kind": "film",
                "artifact": {"path": artifact.name, "sha256": digest},
                "reviews": {
                    "content": {"verdict": "PASS", "sha256": digest, "evidence": content.name},
                    "visual": {"verdict": "PASS", "sha256": digest, "evidence": visual.name},
                },
            }
            record.write_text(json.dumps(details))
            self.assertEqual(check(record), artifact.resolve())

            details["reviews"]["visual"]["verdict"] = "REVISE"
            record.write_text(json.dumps(details))
            with self.assertRaisesRegex(ValueError, "visual must have a PASS"):
                check(record)

            details["reviews"]["visual"]["verdict"] = "PASS"
            details["reviews"]["visual"]["evidence"] = "../other.md"
            record.write_text(json.dumps(details))
            with self.assertRaisesRegex(ValueError, "inside the review folder"):
                check(record)

            details["reviews"]["visual"]["evidence"] = content.name
            record.write_text(json.dumps(details))
            with self.assertRaisesRegex(ValueError, "own evidence file"):
                check(record)

            details["reviews"]["visual"]["evidence"] = visual.name
            record.write_text(json.dumps(details))
            artifact.write_bytes(b"new cut")
            with self.assertRaisesRegex(ValueError, "hash no longer matches"):
                check(record)

    def test_privacy_checks_reject_local_inputs(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "example.md").write_text("A lamp guide")
            self.assertEqual(list(scan(root)), [])
            (root / "input.log").write_text("a local log")
            (root / "example.md").write_text(
                "/" + "Users/" + "fictional-person\n"
                + "sk-" + "a" * 24 + "\n"
                + "contact" + "@" + "fictional.invalid\n"
            )
            (root / "asset.bin").write_bytes(b"\xff")
            reasons = [reason for _, reason in scan(root)]
            for expected in ("personal path", "credential-shaped string", "email address", "local artifact", "binary"):
                self.assertTrue(any(expected in reason for reason in reasons), reasons)


if __name__ == "__main__":
    unittest.main()
