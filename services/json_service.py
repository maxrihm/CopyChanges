import json

class JsonService:
    def load_json_file(self, json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return f"Error loading JSON: {e}"
