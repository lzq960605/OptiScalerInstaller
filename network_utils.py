import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_SHARED_RETRY_SESSION = None
_SHARED_RETRY_SESSION_LOCK = threading.Lock()


def build_retry_session(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504), allowed_methods=("GET", "HEAD")):
    session = requests.Session()
    retry_strategy = Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=allowed_methods,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def get_shared_retry_session():
    global _SHARED_RETRY_SESSION

    if _SHARED_RETRY_SESSION is None:
        with _SHARED_RETRY_SESSION_LOCK:
            if _SHARED_RETRY_SESSION is None:
                _SHARED_RETRY_SESSION = build_retry_session()
    return _SHARED_RETRY_SESSION
