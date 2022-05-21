from funcy import last


def get_file_extension(filename: str) -> str:
    return last(filename.split('.'))
