import logging
from contextlib import contextmanager
from socket import timeout
from typing import Callable, Generator

from funcy import compose
from requests import RequestException

from virtual_agent.exceptions import FailedDependency

logger = logging.getLogger(__name__)


def safe_request(
    error_msg: str, raise_as: type[Exception] = FailedDependency
) -> Callable:
    """
    Wraps calls to third-party services, logging network-specific errors
    """

    @contextmanager
    def inner() -> Generator:
        try:
            yield
        except (RequestException, timeout) as e:
            logger.error(error_msg, extra={'error': str(e)})
            raise raise_as(error_msg) from e

    return inner


safe_request_method = compose(staticmethod, safe_request)
