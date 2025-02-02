from typing import IO


def is_non_empty_file(file: IO) -> bool:
    size = file.seek(0, 2)
    file.seek(0)
    return size > 0
