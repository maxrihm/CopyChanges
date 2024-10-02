import os

class FileService:
    def read_file_content(self, full_path):
        if os.path.isfile(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception as e:
                return f"Failed to read {full_path}: {e}"
        return None

    def save_to_file(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(data)
        except Exception as e:
            return f"Failed to save {file_path}: {e}"
