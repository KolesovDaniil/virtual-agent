from typing import Any, Generator

from funcy import invoke, joining, keep


@joining('/')
def join_url_parts(
    *parts: Any, first_slash: bool = True, trailing_slash: bool = True
) -> Generator:
    parts_ = map(str, parts)

    if first_slash:
        yield ''  # adds first slash

    yield from keep(invoke(parts_, 'strip', '/'))

    if trailing_slash:
        yield ''  # adds trailing slash
