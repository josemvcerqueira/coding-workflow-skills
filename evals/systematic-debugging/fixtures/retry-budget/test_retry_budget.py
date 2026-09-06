import unittest

from retry_budget import retry_count


class RetryBudgetTests(unittest.TestCase):
    def test_explicit_zero_disables_retries(self):
        self.assertEqual(0, retry_count({"retry_budget": 0}))


if __name__ == "__main__":
    unittest.main()
