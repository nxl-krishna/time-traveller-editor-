# Time-Travel Line Editor

A lightweight, terminal-based **time-travel line editor** implemented in Python. It lets you load a text file, make line-level edits (replace/insert/delete), and stores a timeline of snapshots so you can preview, checkout, and branch from previous states — similar to a tiny, file-scoped version control timeline.

---

## Key ideas / overview

- Load a file into memory and take a snapshot after each edit.
- Keep a timeline of snapshots (full-file copies) that you can preview or checkout.
- `checkout` lets you revert to a past snapshot and continue editing from there (this implementation truncates any later snapshots, effectively creating a new branch).
- Changes are only written back to disk when you explicitly run `save`, which also creates a `*.bak` backup of the original file.

---

## Features

- Replace, insert, and delete single lines (zero-indexed line numbers).
- Timeline of snapshots with timestamps and short descriptions.
- Preview any past snapshot without modifying the current head.
- Checkout a past snapshot to make it the new head (branching behavior).
- Play through the timeline to review each snapshot.
- Save current state to disk; automatic `.bak` of the original file is created.

---

## Requirements

- Python 3.8+ (should work on most Python 3.x)
- No external Python packages required

---

## Installation / setup

1. Place the script (`editor3.py` or `time_travel_editor.py`) into your working directory.
2. Make sure the script is executable (optional):

```bash
chmod +x editor3.py
```

3. Run:

```bash
python3 editor3.py <path-to-text-file>
```

If the file does not exist, the program will create an empty file and start the session.

**Do not run the editor with `sudo`** unless you specifically need to edit a root-owned file. Running as root can create files owned by root and cause permission problems later.

---

## Commands (interactive)

Commands are typed at the `tt>` prompt. Line numbers are **zero-based** (first line = `0`).

- `s` — show current file state (with numbered lines)
- `t` — show timeline (list of all snapshots)
- `p <i>` — preview snapshot index `i` (view but do not change head)
- `c <i>` — checkout snapshot `i` and create a new head (branching)
- `r <n>` — replace line `n` (you will be prompted for the new single-line text)
- `i <n>` — insert a new line **before** line `n` (prompted for text). To append at end, insert at index = number of lines.
- `d <n>` — delete line `n` (asks confirmation)
- `play` — sequentially show every snapshot in the timeline
- `save` — write current head to disk; a backup `<file>.bak` is created containing the original file
- `q` — quit the editor
- `h` — show this help text inside the program

**Note:** The program accepts commands with numeric arguments in the form `r 2` (you only need to type the number once). If you encounter a prompt that repeats the number, update to the latest script version which accepts the numeric argument directly.

---

## Example session

1. Start the editor:

```bash
python3 editor3.py test.txt
```

2. Show file and edit:

```
tt> s
tt> r 2            # replace line 2 (3rd line)
New text (replace): This is the updated third line
tt> i 1            # insert before line 1
New text (insert): Inserted new line here
tt> t              # view timeline of snapshots
tt> p 0            # preview original
tt> c 0            # checkout original and create new head
tt> save           # write current state to disk and create test.txt.bak
tt> q
```

---

## Behavior notes & gotchas

- **Zero-indexed lines**: The first line of the file is line `0`.
- **Backups**: `save` writes a `.bak` file containing the original contents loaded when the program started.
- **Checkout truncation**: In this implementation, `checkout` will truncate any snapshots that came after the chosen index and then append a fresh snapshot copied from the checked-out state. If you want to preserve the later snapshots, preview (`p <i>`) first and save copies externally before checking out.
- **Permissions**: If `save` fails due to permission errors, ensure the file is owned by your user or run the program in a directory where you have write privileges.

---

## Troubleshooting

- **`AttributeError: 'TimelineEditor' object has no attribute 'current_index'`**: This indicates an older copy of the script that didn't initialize `current_index` early enough. Replace with the fixed script where `self.current_index = -1` is set in `__init__` before the first `push_snapshot()` call.

- **`Invalid line number` / `Invalid index` responses**: Update to the fixed helper `prompt_int()` which accepts numeric arguments passed with the command (e.g. `r 2`) and avoids asking you to re-type numbers.

- **Files becoming owned by root after running with sudo**: Restore ownership to your user:

```bash
sudo chown $USER:$USER <file> <file>.bak
```

---

## Further improvements / roadmap

- Store diffs instead of full snapshots to save memory for large files.
- Add multi-line editing, paste, and block operations.
- Add `git` integration to produce commits with generated commit messages.
- Provide an ncurses or web UI with a real slider for scrubbing timeline states.
- Add branch naming and non-destructive branching of timelines (preserve future snapshots when checking out).
- Integrate language-aware refactors or LLM-based natural-language edits.

---

## Contributing

Contributions are welcome. If you want a change (feature, bugfix, or documentation), create an issue or open a pull request. Keep changes small and include tests/examples where relevant.

---

## License

This project is released under the MIT License. See `LICENSE` for details (or add one if you prefer a different license).

---

*Generated: 2025-08-31 — Simple Time-Travel Line Editor README*

