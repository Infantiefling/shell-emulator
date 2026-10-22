"""Разбор и выполнение команд виртуальной оболочки."""

import posixpath


MAX_PATH_ARGUMENTS = 1
MV_ARGUMENTS = 2


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

    def command_rmdir(self, args):
        """Удалить пустой каталог только из оперативной памяти."""
        path = self.resolve_path(args[0])
        if path not in self.vfs:
            return f"rmdir: no such directory: {path}"
        if self.vfs[path]["type"] != "dir":
            return f"rmdir: not a directory: {path}"
        if path == "/" or self.cwd == path:
            return f"rmdir: cannot remove current or root directory: {path}"
        if any(name.startswith(path + "/") for name in self.vfs):
            return f"rmdir: directory not empty: {path}"
        del self.vfs[path]
        return ""

    def destination_path(self, source, target):
        """Разрешить перемещение в каталог или переименование."""
        dest = self.resolve_path(target)
        if dest in self.vfs and self.vfs[dest]["type"] == "dir":
            return posixpath.join(dest, posixpath.basename(source))
        return dest

    def check_move(self, source, dest):
        """Проверить, допустимо ли перемещение элемента."""
        if source not in self.vfs:
            return f"mv: no such file or directory: {source}"
        if source == "/":
            return "mv: cannot move root directory"
        if dest == source:
            return ""
        if dest in self.vfs:
            return f"mv: destination already exists: {dest}"
        parent = posixpath.dirname(dest) or "/"
        if parent not in self.vfs:
            return f"mv: no such directory: {parent}"
        if self.vfs[parent]["type"] != "dir":
            return f"mv: not a directory: {parent}"
        if dest.startswith(source + "/"):
            return "mv: cannot move a directory into itself"
        return ""

    def move_entries(self, source, dest):
        """Перенести запись и всех её потомков на новые пути."""
        paths = [name for name in self.vfs
                 if name == source or name.startswith(source + "/")]
        moved = {dest + name[len(source):]: self.vfs[name]
                 for name in paths}
        for name in paths:
            del self.vfs[name]
        self.vfs.update(moved)

    def command_mv(self, args):
        """Переместить файл или каталог с потомками в памяти."""
        source = self.resolve_path(args[0])
        dest = self.destination_path(source, args[1])
        error = self.check_move(source, dest)
        if error or source == dest:
            return error
        self.move_entries(source, dest)
        if self.cwd == source or self.cwd.startswith(source + "/"):
            self.cwd = dest + self.cwd[len(source):]
        return ""

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
        if command == "du":
            return self.command_du(args), False
        if command == "rmdir":
            return self.command_rmdir(args), False
        return self.command_mv(args), False

    def argument_error(self, command, args):
        """Вернуть описание ошибки аргументов или пустую строку."""
        if command == "mv" and len(args) != MV_ARGUMENTS:
            return "mv: expected source and destination"
        if command == "rmdir" and not args:
            return "rmdir: missing directory operand"
        if command in ("ls", "cd", "du", "rmdir") and (
            len(args) > MAX_PATH_ARGUMENTS
        ):
            return f"{command}: too many arguments"
        if command in ("pwd", "history", "exit") and args:
            return f"{command}: too many arguments"
        return ""

    def execute(self, line):
        """Выполнить ввод и вернуть результат и признак выхода."""
        command, args = parse_command(line)
        if not command:
            return "", False
        self.history.append(line.strip())
        known = ("ls", "cd", "pwd", "du", "history", "exit", "rmdir", "mv")
        if command not in known:
            return f"{command}: command not found", False
        error = self.argument_error(command, args)
        if error:
            return error, False
        return self.run_command(command, args)
