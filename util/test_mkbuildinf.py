import os
from pathlib import Path
import subprocess
import unittest


class BuildinfoTests(unittest.TestCase):
    def test_payload_mode_omits_date_without_changing_normal_builds(self):
        script = Path(__file__).with_name("mkbuildinf.pl")
        results = {}
        for mode in ("0", "1"):
            for epoch in ("1000000000", "1100000000"):
                results[mode, epoch] = subprocess.check_output(
                    ["perl", str(script), "cc flags", "test-platform"],
                    env={**os.environ, "SOURCE_DATE_EPOCH": epoch, "BUILDXL_PAYLOAD_BUILD": mode},
                    text=True,
                )
        self.assertEqual(results["1", "1000000000"], results["1", "1100000000"])
        self.assertIn('DATE "built on: date not recorded"', results["1", "1000000000"])
        self.assertNotEqual(results["0", "1000000000"], results["0", "1100000000"])


if __name__ == "__main__":
    unittest.main()
