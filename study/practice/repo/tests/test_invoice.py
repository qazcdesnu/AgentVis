import unittest

from invoice import total


class TotalTest(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(total([1.0, 2.5]), 3.5)

    def test_code_is_case_insensitive(self):
        self.assertEqual(total([100.0], "save10"), 90.0)


if __name__ == "__main__":
    unittest.main()
