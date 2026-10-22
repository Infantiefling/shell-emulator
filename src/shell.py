"""Разбор и выполнение команд виртуальной оболочки."""

import posixpath


def parse_command(line):
    """Разделить ввод на команду и аргументы."""
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


class Shell:
    """Хранить текущий каталог, историю и виртуальные файлы."""

    def __init__(self, vfs):
        self.vfs = vfs
        self.cwd = "/"
        self.history = []

    def resolve_path(self, path):
        """Получить абсолютный путь из относительного или абсолютного."""
        if path.startswith("/"):
            return posixpath.normpath(path)
        return posixpath.normpath(posixpath.join(self.cwd, path))

    def command_ls(self, args):
        """Показать непосредственных потомков каталога."""
        path = self.resolve_path(args[0]) if args else self.cwd
        if path not in self.vfs:
            return f"ls: no such file or directory: {path}"
        if self.vfs[path]["type"] == "file":
            return posixpath.basename(path)
        names = []
        for item in self.vfs:
            if item != path and posixpath.dirname(item) == path:
                names.append(posixpath.basename(item))
        return "\n".join(sorted(names))

    def command_cd(self, args):
        """Изменить текущий каталог оболочки."""
        path = self.resolve_path(args[0]) if args else "/"
        if path not in self.vfs:
            return f"cd: no such directory: {path}"
        if self.vfs[path]["type"] != "dir":
            return f"cd: not a directory: {path}"
        self.cwd = path
        return ""

    def command_du(self, args):
        """Посчитать размер файла или каталога в байтах."""
        path = self.resolve_path(args[0]) if args else self.cwd
        if path not in self.vfs:
            return f"du: no such file or directory: {path}"
        if self.vfs[path]["type"] == "file":
            size = len(self.vfs[path]["content"])
        else:
            prefix = path.rstrip("/") + "/"
            size = 0
            for name, entry in self.vfs.items():
                if name.startswith(prefix) and entry["type"] == "file":
                    size += len(entry["content"])
        return f"{size}\t{path}"

    def run_command(self, command, args):
        """Выполнить распознанную команду оболочки."""
        if command == "exit":
            return "", True
        if command == "pwd":
            return self.cwd, False
        if command == "history":
            lines = [f"{i}  {text}" for i, text in
                     enumerate(self.history, start=1)]
            return "\n".join(lines), False
        if command == "ls":
            return self.command_ls(args), False
        if command == "cd":
            return self.command_cd(args), False
        return self.command_du(args), False

    def execute(self, line):
        """Выполнить ввод и вернуть результат и признак выхода."""
        command, args = parse_command(line)
        if not command:
            return "", False
        self.history.append(line.strip())
        if command not in ("ls", "cd", "pwd", "du", "history", "exit"):
            return f"{command}: command not found", False
        if command in ("ls", "cd", "du") and len(args) > 1:
            return f"{command}: too many arguments", False
        if command in ("pwd", "history", "exit") and args:
            return f"{command}: too many arguments", False
        return self.run_command(command, args)
