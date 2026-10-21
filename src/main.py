"""Tkinter GUI for the shell emulator."""

import getpass
import socket
import tkinter as tk

from shell import execute


class ShellWindow:
    """Simple interactive shell window."""

    def __init__(self, root):
        self.root = root
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
        self.write("Shell emulator (stage 1)\n")

    def write(self, text):
        """Append text to the read-only terminal transcript."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.configure(state="disabled")
        self.output.see("end")

    def on_enter(self, _event=None):
        """Execute the entered command and display its result."""
        line = self.entry.get()
        self.entry.delete(0, "end")
        self.write(f"{self.user}@{self.host}:~$ {line}\n")
        result, should_exit = execute(line)
        if result:
            self.write(result + "\n")
        if should_exit:
            self.root.destroy()


def main():
    root = tk.Tk()
    ShellWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
