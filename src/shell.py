"""Command parsing and first-stage shell stubs."""


def parse_command(line):
    """Split input into a command and its arguments."""
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def execute(line):
    """Return command output and whether the application should close."""
    command, args = parse_command(line)
    if not command:
        return "", False

    if command in ("ls", "cd"):
        if len(args) > 1:
            return f"{command}: too many arguments", False
        return f"{command}: args={args}", False

    if command == "exit":
        if args:
            return "exit: too many arguments", False
        return "", True

    return f"{command}: command not found", False
