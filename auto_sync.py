"""
Auto-Sync Watcher for Walmart Sales Analytics Project.
Automatically detects file changes, commits them, and pushes to GitHub.
"""

import os
import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IGNORED_PATTERNS = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".idea",
    ".vscode",
    "models/final_model.pkl",
    "models/final_model.joblib",
    ".tmp",
    ".swp",
    "auto_sync.py",
]

def run_cmd(cmd):
    """Run a shell command and return stdout/returncode."""
    try:
        res = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def sync_to_github():
    """Stage, commit, and push changes to GitHub if any exist."""
    ret, status_out, _ = run_cmd("git status --porcelain")
    if not status_out:
        return False

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Detected project changes:")
    for line in status_out.splitlines()[:5]:
        print(f"   {line}")
    if len(status_out.splitlines()) > 5:
        print(f"   ... and {len(status_out.splitlines()) - 5} more files")

    # Add all changed files (respecting .gitignore)
    run_cmd("git add .")

    # Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-update: {timestamp}"
    ret, commit_out, commit_err = run_cmd(f'git commit -m "{commit_msg}"')
    if ret != 0 and "nothing to commit" in (commit_out + commit_err).lower():
        return False

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Committed: '{commit_msg}'")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushing to GitHub (origin main)...")

    # Push to GitHub
    ret, push_out, push_err = run_cmd("git push origin main")
    if ret == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully pushed to GitHub!")
        return True
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Push failed (will retry on next change): {push_err}")
        return False


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, debounce_sec=15):
        super().__init__()
        self.debounce_sec = debounce_sec
        self.last_change_time = 0
        self.pending = False

    def on_any_event(self, event):
        path = event.src_path.replace("\\", "/")
        if any(ign in path for ign in IGNORED_PATTERNS):
            return
        self.last_change_time = time.time()
        self.pending = True


def main():
    print("=" * 60)
    print(" GitHub Auto-Sync Watcher Started")
    print(" Repository: thamizharasanm2528-byte/Data_Analytics_Project_RetailPrice")
    print("=" * 60)
    print("Monitoring project for edits...")
    print("Changes will be automatically committed & pushed after a 15s debounce.")
    print("Press Ctrl+C to stop.\n")

    handler = ChangeHandler(debounce_sec=15)
    observer = Observer()
    observer.schedule(handler, path=".", recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(2)
            if handler.pending and (time.time() - handler.last_change_time >= handler.debounce_sec):
                handler.pending = False
                sync_to_github()
    except KeyboardInterrupt:
        print("\nStopping Auto-Sync Watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
