#!/usr/bin/env python3
"""
Time-travel line editor (fixed)
"""

import sys
import copy
import time
from datetime import datetime

def read_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().splitlines()

def write_file(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
        if lines and not lines[-1].endswith("\n"):
            f.write("\n")

def show_lines(lines):
    for i, ln in enumerate(lines):
        print(f"{i:3d}: {ln}")

class TimelineEditor:
    def __init__(self, path):
        self.path = path
        self.original = read_file(path)
        self.snapshots = []  # list of dicts: { 'time':..., 'desc':..., 'lines':[...] }
        # initialize before calling push_snapshot
        self.current_index = -1
        self.push_snapshot(self.original, "Loaded original file")

    def push_snapshot(self, lines, desc="edit"):
        if not hasattr(self, 'current_index'):
            self.current_index = -1

        snap = {
            'time': datetime.now().isoformat(sep=' ', timespec='seconds'),
            'desc': desc,
            'lines': copy.deepcopy(lines)
        }
        if self.current_index < len(self.snapshots) - 1:
            self.snapshots = self.snapshots[:self.current_index+1]
        self.snapshots.append(snap)
        self.current_index = len(self.snapshots) - 1

    def current_lines(self):
        return copy.deepcopy(self.snapshots[self.current_index]['lines'])

    def show_current(self):
        print("\n=== Current file state (index", self.current_index, ") ===")
        show_lines(self.current_lines())
        print("=== end ===\n")

    def replace_line(self, lineno, new_text):
        lines = self.current_lines()
        if 0 <= lineno < len(lines):
            old = lines[lineno]
            lines[lineno] = new_text
            self.push_snapshot(lines, f"Replace line {lineno}: '{old}' -> '{new_text}'")
            print("Replaced.")
        else:
            print("Line number out of range.")

    def insert_line(self, lineno, new_text):
        lines = self.current_lines()
        if 0 <= lineno <= len(lines):
            lines.insert(lineno, new_text)
            self.push_snapshot(lines, f"Insert at {lineno}: '{new_text}'")
            print("Inserted.")
        else:
            print("Line number out of range.")

    def delete_line(self, lineno):
        lines = self.current_lines()
        if 0 <= lineno < len(lines):
            old = lines.pop(lineno)
            self.push_snapshot(lines, f"Delete line {lineno}: '{old}'")
            print("Deleted.")
        else:
            print("Line number out of range.")

    def timeline(self):
        print("\n--- Timeline ---")
        for i, s in enumerate(self.snapshots):
            indicator = "<-- current" if i == self.current_index else ""
            desc = s['desc'] if len(s['desc']) < 60 else s['desc'][:57] + '...'
            print(f"{i:3d} | {s['time']} | {desc:60} {indicator}")
        print("--- end ---\n")

    def preview_state(self, index):
        if 0 <= index < len(self.snapshots):
            print(f"\n--- Preview state {index} ({self.snapshots[index]['time']}) ---")
            show_lines(self.snapshots[index]['lines'])
            print("--- end preview ---\n")
        else:
            print("Index out of range.")

    def checkout(self, index):
        if 0 <= index < len(self.snapshots):
            self.current_index = index
            self.push_snapshot(self.current_lines(), f"Checkout state {index} as new head")
            print(f"Checked out state {index} and created new head at index {self.current_index}.")
        else:
            print("Index out of range.")

    def save(self):
        bak = self.path + ".bak"
        try:
            write_file(bak, self.original)
        except Exception as e:
            print("Warning: couldn't write backup:", e)
        try:
            write_file(self.path, self.current_lines())
            print(f"Saved current state to {self.path} (backup -> {bak})")
        except Exception as e:
            print("Error writing file:", e)

    def play(self, delay=0.6):
        print("Playing timeline forward from 0 to tip:")
        for i in range(len(self.snapshots)):
            print(f"\n---- state {i} ({self.snapshots[i]['time']}) ----")
            show_lines(self.snapshots[i]['lines'])
            time.sleep(delay)
        print("Play finished.\n")

def prompt_int(prompt):
    """
    Accept either:
      - a numeric string supplied as `prompt` (e.g. '2') -> returns int(2)
      - or a prompt string to show to the user (e.g. 'Enter line: ') -> waits for input
    Returns integer or None on failure.
    """
    try:
        # if caller passed a numeric string like '2', use it directly
        return int(prompt.strip())
    except Exception:
        try:
            # otherwise treat `prompt` as a prompt text to show, and read input
            return int(input(prompt).strip())
        except Exception:
            return None


def main_loop(editor: TimelineEditor):
    print("Simple Time-Travel Editor")
    helptext = """
Commands:
  s        : show current file state
  t        : show timeline
  p <i>    : preview state index i
  c <i>    : checkout state i (branch from past)
  r <n>    : replace line n (will prompt for text)
  i <n>    : insert before line n (will prompt for text)
  d <n>    : delete line n
  play     : play through timeline
  save     : save current to disk (creates .bak)
  q        : quit
  h        : show this help
"""
    print(helptext)
    while True:
        cmdline = input("tt> ").strip()
        if not cmdline:
            continue
        parts = cmdline.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == 'h':
            print(helptext)
        elif cmd == 's':
            editor.show_current()
        elif cmd == 't':
            editor.timeline()
        elif cmd == 'p':
            if len(parts) < 2:
                print("Usage: p <index>")
                continue
            idx = prompt_int(parts[1])
            if idx is None:
                print("Invalid index.")
                continue
            editor.preview_state(idx)
        elif cmd == 'c':
            if len(parts) < 2:
                print("Usage: c <index>")
                continue
            idx = prompt_int(parts[1])
            if idx is None:
                print("Invalid index.")
                continue
            editor.checkout(idx)
        elif cmd == 'r':
            if len(parts) < 2:
                print("Usage: r <line_number>")
                continue
            ln = prompt_int(parts[1])
            if ln is None:
                print("Invalid line number.")
                continue
            newt = input("New text (replace): ")
            editor.replace_line(ln, newt)
        elif cmd == 'i':
            if len(parts) < 2:
                print("Usage: i <line_number>")
                continue
            ln = prompt_int(parts[1])
            if ln is None:
                print("Invalid line number.")
                continue
            newt = input("New text (insert): ")
            editor.insert_line(ln, newt)
        elif cmd == 'd':
            if len(parts) < 2:
                print("Usage: d <line_number)")
                continue
            ln = prompt_int(parts[1])
            if ln is None:
                print("Invalid line number.")
                continue
            confirm = input(f"Delete line {ln}? (y/N): ").lower()
            if confirm == 'y':
                editor.delete_line(ln)
            else:
                print("Cancelled.")
        elif cmd == 'play':
            try:
                d = float(input("Delay seconds between steps (default 0.6): ") or "0.6")
            except:
                d = 0.6
            editor.play(delay=d)
        elif cmd == 'save':
            editor.save()
        elif cmd == 'q':
            print("Bye.")
            break
        else:
            print("Unknown command. Type 'h' for help.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 time_travel_editor.py <file>")
        sys.exit(1)
    path = sys.argv[1]
    try:
        ed = TimelineEditor(path)
    except FileNotFoundError:
        print("File not found. Creating new empty file.")
        open(path, 'w').close()
        ed = TimelineEditor(path)
    main_loop(ed)

