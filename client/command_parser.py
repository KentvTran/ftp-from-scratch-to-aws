import os

def parse_command(line):
    if not line:
        return None, None, "Empty command"

    parts = line.strip().split()
    cmd = parts[0].upper()

    if cmd == "LS":
        return "LS", {}, None

    if cmd == "GET":
        if len(parts) < 2:
            return None, None, "Usage: GET <filename>"
        return "GET", {"filename": parts[1]}, None

    if cmd == "PUT":
        if len(parts) < 2:
            return None, None, "Usage: PUT <filename>"
        fn = parts[1]
        if not os.path.isfile(fn):
            return None, None, f"File not found: {fn}"
        return "PUT", {"filename": fn}, None

    if cmd == "EXIT":
        return "EXIT", {}, None

    return None, None, f"Unknown command: {cmd}"