import json
import unittest
import os
from typing import Callable, Optional

import noclist

TEST_SERVER = os.environ.get('NOCLIST_TEST_SERVER', None)

def fail_n_times(n: int) -> Callable[[], Optional[str]]:
    """Return a closure that returns None the first n times it is
    invoked and "ok" subsequently. This is for testing the retry
    function.
    """
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
        # This is a sort of property based test. It could be better
        # formulated using a framework like hypothesis.
        for tries in range(4):
            for fails in range(5):
                self.assertEqual(
                    noclist.retry(fail_n_times(fails), tries),
                    "ok" if fails < tries else None,
                )

class TestChecksum(unittest.TestCase):
    def test_example(self):
        # This is the example checksum calculation given in the
        # documentation.
        self.assertEqual(
            noclist.checksum("12345", "users"),
            "c20acb14a3d3339b9e92daebb173e41379f9f2fad4aa6a6326a696bd90c67419"
        )

    def test_nonascii(self):
        # Make sure it rejects non ascii input.
        self.assertRaises(UnicodeEncodeError, lambda: noclist.checksum("😊", "users"))
        self.assertRaises(UnicodeEncodeError, lambda: noclist.checksum("12345", "😊"))

@unittest.skipIf(TEST_SERVER is None, "No test server provided.")
class TestWithServer(unittest.TestCase):
    def test_noclist(self):
        code, output = noclist.noclist(TEST_SERVER)
        self.assertEqual(code, 0)
        decoded = json.loads(output)
        # Not much is specified about the test server except it
        # returns valid data.  It looks like it always returns the
        # same result, but I don't want to rely on that. Ideally one
        # would write a mock server that produces known results and
        # can even reproduce the errors typical of the real server.
        self.assertEqual(type(decoded), list)


if __name__ == '__main__':
    unittest.main()

