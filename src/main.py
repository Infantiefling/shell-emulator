"""Графический интерфейс эмулятора на Tkinter."""

import getpass
import socket
import tkinter as tk

from config import load_config, read_startup_script
from shell import execute
from vfs import load_vfs, VFSError


class ShellWindow:
    """Окно эмулятора с поддержкой стартового скрипта."""

    def __init__(self, root, config, vfs):
        self.root = root
        self.vfs = vfs
        self.user = getpass.getuser()
        self.host = socket.gethostname()
        root.title(f"Эмулятор - [{self.user}@{self.host}]")
        root.geometry("800x480")

        self.output = tk.Text(root, state="disabled", wrap="word")
        self.output.pack(fill="both", expand=True, padx=8, pady=8)
        self.entry = tk.Entry(root)
        self.entry.pack(fill="x", padx=8, pady=(0, 8))
        self.entry.bind("<Return>", self.on_enter)
        self.entry.focus_set()
        self.write("Shell emulator (stage 3)\n")
        self.show_config(config)
        self.show_vfs()
        if config.script:
            root.after(0, self.run_script, config.script)

    def write(self, text):
        """Добавить текст в область вывода команд."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.configure(state="disabled")
        self.output.see("end")

    def show_config(self, config):
        """Показать итоговые параметры запуска."""
        self.write(f"VFS: {config.vfs}\n")
        self.write(f"Script: {config.script}\n")
        self.write(f"Config: {config.config}\n")

    def show_vfs(self):
        """Показать загруженные элементы VFS для проверки."""
        self.write(f"VFS entries: {len(self.vfs)}\n")
        for path, entry in sorted(self.vfs.items()):
            self.write(f"  {entry['type']}: {path}\n")

    def process_line(self, line):
        """Показать команду и результат её выполнения."""
        self.write(f"{self.user}@{self.host}:~$ {line}\n")
        result, should_exit = execute(line)
        if result:
            self.write(result + "\n")
        if should_exit:
            self.root.destroy()
        return should_exit

    def on_enter(self, _event=None):
        """Обработать команду, введённую в окне."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.process_line(line)

    def run_script(self, path):
        """Выполнить команды скрипта по порядку в окне."""
        try:
            commands = read_startup_script(path)
        except ValueError as error:
            self.write(f"{error}\n")
            return
        for line in commands:
            if self.process_line(line):
                return


def main():
    """Загрузить конфигурацию и запустить приложение."""
    try:
        config = load_config()
    except ValueError as error:
        raise SystemExit(str(error)) from error
    try:
        vfs = load_vfs(config.vfs)
    except VFSError as error:
        raise SystemExit(str(error)) from error
    root = tk.Tk()
    ShellWindow(root, config, vfs)
    root.mainloop()


if __name__ == "__main__":
    main()
