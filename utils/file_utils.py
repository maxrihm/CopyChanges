# utils/file_utils.py

import os


def read_file_content(full_path):
    if os.path.isfile(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"Failed to read {full_path}: {e}"
    return None
