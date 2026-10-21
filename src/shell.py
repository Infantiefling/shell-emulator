"""Разбор команд и заглушки первого этапа."""


def parse_command(line):
    """Разделить ввод на команду и аргументы."""
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def execute(line):
    """Вернуть результат команды и признак завершения программы."""
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
