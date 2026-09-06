"""Root entrypoint for the repository's complete unittest suite."""

import unittest

from skills.test_all import load_tests


if __name__ == "__main__":
    unittest.main(module=__name__)
