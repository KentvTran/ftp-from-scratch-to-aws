from __future__ import annotations

import re
from typing import Iterable

# Control ports
CONTROL_PORT = 21
FALLBACK_CONTROL_PORT = 2121  

# Data port range
DATA_PORT_LOW = 20000
DATA_PORT_HIGH = 21000

# Socket settings
ENCODING = "utf-8"
LINE_TERMINATOR = "\n"
BUFFER_SIZE = 64 * 1024  # 64 KiB chunks.
SOCKET_TIMEOUT = 60  # seconds

# Response codes
RESP_OK = "200"
RESP_DONE = "226"
RESP_CLIENT_ERROR = "500"
RESP_NOT_FOUND = "550"

# Filename checker
FILENAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def is_valid_filename(name: str) -> bool:
    """True if name uses allowed characters."""
    return bool(FILENAME_PATTERN.fullmatch(name))


def build_response(code: str, *parts: Iterable[object]) -> str:
    """Make one response line."""
    tokens = [code]
    for part in parts:
        if part is None:
            continue
        tokens.append(str(part))
    return " ".join(tokens) + LINE_TERMINATOR


def parse_response(line: str) -> list[str]:
    """Split response into tokens."""
    return line.strip().split()
