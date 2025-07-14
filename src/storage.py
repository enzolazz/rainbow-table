import json
from pathlib import Path
from typing import Any, Dict


class JSONStorage:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path

    def save(self, data: Dict[str, Any]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
