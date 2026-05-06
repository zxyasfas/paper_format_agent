from __future__ import annotations

import unittest

from tools.validate_skill import validate_skill


class SkillMetadataTests(unittest.TestCase):
    def test_skill_metadata_is_valid(self):
        validate_skill()


if __name__ == "__main__":
    unittest.main()
