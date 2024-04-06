import json
import logging
import hashlib
import optparse
import requests
from requests import RequestException
import sys
from typing import Callable, Optional, TypeVar

REQUEST_TRIES = 3 # Number of times to attempt BADSEC requests.
REQUEST_TIMEOUT = 5 # Timeout in secs for BADSEC requests.


T = TypeVar('T')
def retry(f: Callable[[], Optional[T]], n_tries: int) -> Optional[T]:
    """Retry the function f up to n_tries times. Returns the first non-None
    result of f() or None if all tries are exhausted.
    """
    while n_tries > 0:
        result = f()
        if result is not None:
            return result
        n_tries -= 1
    return None

def get_auth(url: str) -> Optional[str]:
    """Get the auth token from a BADSEC server based at the given url.
    Returns the token on success and None on failure.
    """
    def attempt() -> Optional[str]:
        logging.info("requesting auth token")
        try:
            r = requests.get(f"{url}/auth", timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
        except RequestException as e:
            logging.debug("auth token request failed: %s", e)
            return None
        return r.headers["Badsec-Authentication-Token"]

    return retry(attempt, REQUEST_TRIES)

def checksum(token: str, path: str) -> str:
    """Return the checksum for a BADSEC server request for the given
    path using the given auth token. Supports only ascii strings
    for the token and path.
    """
    return hashlib.sha256(f"{token}/{path}".encode('ascii')).hexdigest()

def get_users(url: str, token: str) -> Optional[list[str]]:
    """Get the list of users from a BADSEC server based at the given
    url using the given auth token. Returns a list of the user ids on
    success and None on failure. Will retry the request up to a total
    of REQUEST_TRIES attempts.
    """
    cs = checksum(token, "users")

    def attempt() -> Optional[list[str]]:
        logging.info("requesting user list")
        try:
            r = requests.get(
                f"{url}/users",
                headers={"X-Request-Checksum": cs},
                timeout=REQUEST_TIMEOUT
            )
            r.raise_for_status()
        except RequestException as e:
            logging.debug("user list request failed: %s", e)
            return None
        return r.text.split('\n')

    return retry(attempt, REQUEST_TRIES)

def noclist(url: str) -> int:
    """Retrieve the list of users from a BADSEC server based at the
    given url and print the list to stdout as a JSON list. Returns
    0 on success and 1 on failure.
    """
    token = get_auth(url)
    if token is None:
        logging.error("failed to get auth token")
        return 1

    users = get_users(url, token)
    if users is None:
        logging.error("failed to get user list")
        return 1

    print(json.dumps(users))
    return 0

if __name__ == "__main__":
    parser = optparse.OptionParser(usage="usage: %prog [options] BADSEC_SERVER_URL")
    parser.add_option("-v", dest="verbose", action="store_true", default=False)

    options, args = parser.parse_args()
    if len(args) < 1:
        parser.print_usage()
        exit(0)

    loglevel = logging.DEBUG if options.verbose else logging.WARNING
    logging.basicConfig(stream=sys.stderr, level=loglevel)

    exit(noclist(args[0]))
