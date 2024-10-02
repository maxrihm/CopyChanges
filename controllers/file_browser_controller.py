import os
import json
from services.json_service import JsonService
from services.file_service import FileService

class FileBrowserController:
    def __init__(self, file_browser, project_directory):
        self.file_browser = file_browser  # The FileBrowser widget
        self.project_directory = project_directory
        self.json_service = JsonService()
        self.file_service = FileService()
        self.selection_file = os.path.join(self.project_directory, 'file_selections.json')
        self.selected_files = self.load_checked_files()

    def load_checked_files(self):
        """Load checked files from the JSON file"""
        if os.path.exists(self.selection_file):
            return self.json_service.load_json_file(self.selection_file) or []
        return []

    def save_checked_files(self, checked_files):
        """Save selected files to the JSON file"""
        self.file_service.save_to_file(self.selection_file, json.dumps(checked_files))

    def refresh(self):
        """Refresh the file browser with the selected files loaded from JSON"""
        current_files = self.file_browser.get_all_files()
        refreshed_checked_files = [file for file in self.selected_files if os.path.exists(file)]
        self.save_checked_files(refreshed_checked_files)
        self.file_browser.refresh_checked_items(refreshed_checked_files)

    def handle_file_selection(self):
        """Handle file selection and save the checked files"""
        checked_files = self.file_browser.get_checked_items()
        self.save_checked_files(checked_files)

    def load_directory(self, directory):
        """Delegate loading the directory to the file_browser and refresh checked files"""
        self.file_browser.load_directory(directory)
        self.refresh()  # Refresh the file browser with previously selected files
