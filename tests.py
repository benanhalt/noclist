import unittest
import noclist
from typing import Callable, Optional

def fail_n_times(n: int) -> Callable[[], Optional[str]]:
    fails = 0
    def f() -> Optional[str]:
        nonlocal fails
        if n > fails:
            fails += 1
            return None
        else:
            return "ok"
    return f

class TestRetry(unittest.TestCase):
    def test_retry(self):
        for tries in range(4):
            for fails in range(5):
                self.assertEqual(
                    noclist.retry(fail_n_times(fails), tries),
                    "ok" if fails < tries else None,
                )

class TestChecksum(unittest.TestCase):
    def test_example(self):
        self.assertEqual(
            noclist.checksum("12345", "users"),
            "c20acb14a3d3339b9e92daebb173e41379f9f2fad4aa6a6326a696bd90c67419"
        )

    def test_nonascii(self):
        self.assertRaises(UnicodeEncodeError, lambda: noclist.checksum("😊", "users"))
        self.assertRaises(UnicodeEncodeError, lambda: noclist.checksum("12345", "😊"))


if __name__ == '__main__':
    unittest.main()

