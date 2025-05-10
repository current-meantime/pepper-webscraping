import json

class DataSaver:
    """Handles saving scraped data to JSON files."""
    @staticmethod
    def save_data_to_json(data, file_path):
        """Saves data to a JSON file."""

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {file_path}")
        return data