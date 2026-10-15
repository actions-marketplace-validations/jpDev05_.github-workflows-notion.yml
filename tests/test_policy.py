import tempfile
import unittest

from scripts.policy import load_policy


class PolicyLoaderTests(unittest.TestCase):
    def test_loads_repository_policy(self):
        content = """version: 1

review:
  language: pt-BR
  profile: strict
  max_inline_findings: 5
  min_score: 8
  fail_on_high_risk: true

pull_request:
  event: REQUEST_CHANGES

paths:
  ignore:
    - "dist/**"
    - "*.lock"
"""

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            suffix=".yml",
            delete=False,
        ) as handle:
            handle.write(content)
            path = handle.name

        try:
            policy = load_policy(path)
        finally:
            import os
            os.unlink(path)

        self.assertEqual(policy["review"]["profile"], "strict")
        self.assertEqual(policy["review"]["max_inline_findings"], 5)
        self.assertEqual(policy["review"]["min_score"], 8)
        self.assertTrue(policy["review"]["fail_on_high_risk"])
        self.assertEqual(policy["pull_request"]["event"], "REQUEST_CHANGES")
        self.assertEqual(policy["paths"]["ignore"], ["dist/**", "*.lock"])

    def test_missing_file_returns_safe_defaults(self):
        policy = load_policy("/tmp/ai-devops-policy-does-not-exist.yml")

        self.assertEqual(policy["review"]["min_score"], 0)
        self.assertFalse(policy["review"]["fail_on_high_risk"])
        self.assertEqual(policy["pull_request"]["event"], "COMMENT")


if __name__ == "__main__":
    unittest.main()
import tempfile, os
from scripts.policy import load_policy

def test_policy_loads_core_values():
    data="version: 1\nreview:\n  min_score: 7\n  fail_on_high_risk: true\npull_request:\n  event: REQUEST_CHANGES\n"
    with tempfile.NamedTemporaryFile("w",delete=False,encoding="utf-8") as f:
        f.write(data); path=f.name
    try:
        p=load_policy(path)
        assert p["review"]["min_score"] == 7
        assert p["review"]["fail_on_high_risk"] is True
        assert p["pull_request"]["event"] == "REQUEST_CHANGES"
    finally:
        os.unlink(path)

def test_missing_policy_is_safe():
    p=load_policy("/tmp/does-not-exist-ai-devops.yml")
    assert p["review"]["min_score"] == 0
    assert p["review"]["fail_on_high_risk"] is False
