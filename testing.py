import os
import shutil
import subprocess
import sys

REPO_URL = "https://github.com/Johnmeftah/test_repo.git"
LOCAL_REPO = "/Users/johnmeftah/test_repo"  # change if your clone lives elsewhere
DESKTOP_DIR = "/Users/johnmeftah/Desktop"

def run_git(args, cwd, check=True, capture_output=True):
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        check=check,
        capture_output=capture_output,
        text=True
    )

def ensure_repo():
    if not os.path.isdir(LOCAL_REPO):
        print(f"Local repo not found at {LOCAL_REPO}. Cloning...")
        subprocess.run(["git", "clone", REPO_URL, LOCAL_REPO], check=True)
    elif not os.path.isdir(os.path.join(LOCAL_REPO, ".git")):
        raise RuntimeError(f"{LOCAL_REPO} exists but is not a git repo.")
    else:
        # Optional: fetch to ensure remotes/branches are up to date
        run_git(["fetch", "--all", "--prune"], cwd=LOCAL_REPO, check=False)

def push_file_to_github():
    filename = input("Enter the filename (with extension): ").strip()
    if not filename:
        print("No filename provided.")
        return

    src_path = os.path.join(DESKTOP_DIR, filename)
    if not os.path.exists(src_path):
        print(f"Error: {src_path} does not exist.")
        return

    ensure_repo()

    dest_path = os.path.join(LOCAL_REPO, filename)
    # Create any needed subfolders in the repo if user typed paths like folder/file.txt
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

    # Copy using Python (more portable than calling `cp`)
    shutil.copy2(src_path, dest_path)
    print(f"Copied to repo: {dest_path}")

    # Stage file
    run_git(["add", filename], cwd=LOCAL_REPO)

    # Commit only if there are staged changes
    status = run_git(["status", "--porcelain"], cwd=LOCAL_REPO).stdout.strip()
    if status:
        msg = f"Add/update {filename}"
        run_git(["commit", "-m", msg], cwd=LOCAL_REPO)
        print(f"Committed: {msg}")
    else:
        print("Nothing to commit (file unchanged).")

    # Push (let git decide the current branch, typically 'main' or 'master')
    try:
        run_git(["push"], cwd=LOCAL_REPO)
