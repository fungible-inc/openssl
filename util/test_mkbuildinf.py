import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class BuildinfoTests(unittest.TestCase):
    def test_make_passes_policy_as_an_explicit_option(self):
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(
                ["perl", str(repository / "Configure"), "linux-x86_64", "no-shared", "no-tests"],
                cwd=directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            header = Path(directory) / "crypto/buildinf.h"
            for mode in ("1", "0", ""):
                if header.exists():
                    header.unlink()
                subprocess.run(
                    ["make", "-s", "crypto/buildinf.h", f"SUPPRESS_MOST_TIMESTAMPS={mode}"],
                    cwd=directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                self.assertEqual("date not recorded" in header.read_text(), mode == "1")

    def test_suppression_omits_date_without_changing_normal_builds(self):
        script = Path(__file__).with_name("mkbuildinf.pl")
        results = {}
        for mode in ("0", "1"):
            for epoch in ("1000000000", "1100000000"):
                results[mode, epoch] = subprocess.check_output(
                    ["perl", str(script), *(["--no-generation-stamp"] if mode == "1" else []),
                     "cc flags", "test-platform"],
                    env={**os.environ, "SOURCE_DATE_EPOCH": epoch,
                         "SUPPRESS_MOST_TIMESTAMPS": "0" if mode == "1" else "1",
                         "BUILDXL_PAYLOAD_BUILD": "1"},
                    text=True,
                )
        self.assertEqual(results["1", "1000000000"], results["1", "1100000000"])
        self.assertIn('DATE "built on: date not recorded"', results["1", "1000000000"])
        self.assertNotEqual(results["0", "1000000000"], results["0", "1100000000"])


if __name__ == "__main__":
    unittest.main()
