# utils/git_utils.py

import subprocess


def get_git_changes(project_directory):
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_directory,
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = result.stdout.splitlines()
        file_paths = [file[3:] for file in changed_files if len(file) > 3]
        return file_paths
    except subprocess.CalledProcessError as e:
        return f"Failed to get Git changes: {e}"
