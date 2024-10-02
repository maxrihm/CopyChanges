from PyQt5.QtWidgets import QFileDialog
from services.file_service import FileService
from services.git_service import GitService
from services.json_service import JsonService
from controllers.file_browser_controller import FileBrowserController
import os
import json
import config
import pyperclip

class MainController:
    def __init__(self, view):
        self.view = view
        self.project_directory = ""
        self.editors = view.editors

        # Service instances
        self.file_service = FileService()
        self.git_service = GitService()
        self.json_service = JsonService()

        self.file_browser_controller = None  # Initialize after directory is selected
        self.save_file = config.SAVE_FILE

        # Status update
        self.view.update_status("Please select a project directory to load content.", error=False)
        self.view.update_project_directory_label("Project Directory: Not Set")

    def browse_project_directory(self):
        try:
            directory = QFileDialog.getExistingDirectory(self.view, "Select Project Directory")
            if directory:
                self.project_directory = directory
                self.view.update_project_directory_label(self.project_directory)

                # Initialize FileBrowserController with selected directory and file_browser view
                self.file_browser_controller = FileBrowserController(self.view.file_browser, self.project_directory)

                # Delegate the directory loading to FileBrowserController
                self.file_browser_controller.load_directory(directory)
                self.load_content()
                self.save_content()
            else:
                self.view.update_status("No directory selected.", error=True)
        except Exception as e:
            self.view.update_status(f"Error when selecting folder: {e}", error=True)

    def get_git_changes(self):
        if not self.project_directory:
            self.view.update_status("Please set a valid project directory first.", error=True)
            return

        file_paths = self.git_service.get_git_changes(self.project_directory)
        if isinstance(file_paths, str):
            self.view.update_status(file_paths, error=True)
            return

        self.editors[0].clear()
        for path in file_paths:
            self.editors[0].appendPlainText(path)

    def get_selected_files(self):
        if self.file_browser_controller:
            self.file_browser_controller.handle_file_selection()

    def read_content(self, editor, window_name):
        content = ""
        lines = editor.toPlainText().splitlines()
        for line in lines:
            content += self.process_line(line.strip()) + "\n"

        pyperclip.copy(content)
        self.view.update_status(f"Copied from {window_name}")

    def process_line(self, line):
        if not line:
            return ""
        if line[0].isdigit():
            return self.read_nested_window_content(int(line[0]))
        elif line.startswith('V'):
            return self.handle_v_syntax(line[1:].strip())
        else:
            return self.read_file_content(line)

    def handle_v_syntax(self, json_path):
        json_data = self.json_service.load_json_file(config.SELECTIONS_JSON_PATH)
        if isinstance(json_data, str):
            return json_data

        normalized_json_path = json_path.lower().replace("/", "\\")
        result = ""
        for file_path, file_data in json_data.items():
            if normalized_json_path in file_path.lower():
                file_name = os.path.basename(file_path)
                result += f"Partial content of file {file_name}:\n"
                for item in file_data:
                    result += item['content'] + "\n...\n"
        if not result:
            return f"JSON path {json_path} not found."
        return result

    def read_nested_window_content(self, window_number):
        if 1 <= window_number <= len(self.editors):
            editor = self.editors[window_number - 1]
            return "\n".join(self.process_line(line.strip()) for line in editor.toPlainText().splitlines())
        return ""

    def read_file_content(self, file_path):
        full_path = os.path.join(self.project_directory, file_path)
        content = self.file_service.read_file_content(full_path)
        if content is not None:
            return f"Content of {os.path.basename(full_path)}:\n{content}\n"
        else:
            return file_path

    def save_content(self):
        if not self.project_directory:
            return  # Don't save if no project directory is selected

        data = {
            self.project_directory: {
                f"editor{i+1}_content": editor.toPlainText()
                for i, editor in enumerate(self.editors)
            },
            "last_project_directory": self.project_directory
        }
        self.file_service.save_to_file(self.save_file, json.dumps(data))

    def load_content(self):
        if os.path.exists(self.save_file):
            data = json.loads(self.file_service.read_file_content(self.save_file))
            if self.project_directory in data:
                content = data[self.project_directory]
                for i, editor in enumerate(self.editors):
                    editor.setPlainText(content.get(f"editor{i+1}_content", ""))

    def load_last_workspace(self):
        if os.path.exists(self.save_file):
            data = json.loads(self.file_service.read_file_content(self.save_file))
            self.project_directory = data.get("last_project_directory", "")
            if self.project_directory:
                self.view.update_project_directory_label(self.project_directory)
                self.load_content()

    def close_event(self):
        # Save the content of the editors
        self.save_content()

        # Save selected files from the file browser before closing
        if self.file_browser_controller:
            self.file_browser_controller.handle_file_selection()

