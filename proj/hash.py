import hashlib
from typing import Optional
from .paths import AbsolutePath


def get_file_hash(path: AbsolutePath) -> Optional[bytes]:
    try:
        with path.raw.open("rb") as f:
            digest = hashlib.md5(f.read())
        return digest.digest()
    except FileNotFoundError:
        return None
