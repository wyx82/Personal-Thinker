"""
MemoryManager — JSON memory management with multiple folders.
All operations are folder-aware. _global/ is always accessible.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import USER_DATA_DIR, GLOBAL_DATA_DIR, TEMPLATES_DIR, GLOBAL_FOLDER_NAME


class MemoryManager:
    """Manages all JSON memory operations in a folder system."""

    # Standard files per folder (excluding _global)
    FOLDER_FILES = [
        "conversations.json",
        "problems.json",
        "decisions.json",
        "patterns.json",
        "discoveries.json",
        "learning.json",
    ]

    def __init__(self):
        self.memory_dir = USER_DATA_DIR
        self.global_dir = GLOBAL_DATA_DIR
        self.active_folder: str | None = None
        self._ensure_global_exists()

    # ─── Init ────────────────────────────────────────────────────────────────

    def _ensure_global_exists(self) -> None:
        """Ensure _global/ exists with all necessary files."""
        self.global_dir.mkdir(parents=True, exist_ok=True)

        # Profile
        profile_path = self.global_dir / "profile.json"
        if not profile_path.exists():
            template = TEMPLATES_DIR / "profile.json"
            if template.exists():
                self._copy_template(template, profile_path)

        # Identities
        identitati_path = self.global_dir / "identitati.json"
        if not identitati_path.exists():
            self._copy_template(TEMPLATES_DIR / "identitati.json", identitati_path)

        # Folder connections
        conexiuni_path = self.global_dir / "conexiuni_foldere.json"
        if not conexiuni_path.exists():
            self._copy_template(TEMPLATES_DIR / "conexiuni_foldere.json", conexiuni_path)

    def _copy_template(self, src: Path, dst: Path) -> None:
        """Copy a template to destination."""
        if src.exists():
            import shutil
            shutil.copy2(src, dst)

    # ─── Folder discovery ───────────────────────────────────────────────────

    def get_all_folders(self) -> list[str]:
        """
        Return list of all folders in user_data/,
        excluding _global (which is special).
        """
        if not self.memory_dir.exists():
            return []
        folders = []
        for item in self.memory_dir.iterdir():
            if item.is_dir() and item.name != GLOBAL_FOLDER_NAME:
                folders.append(item.name)
        return sorted(folders)

    def get_active_folder(self) -> str | None:
        """Return current active folder."""
        return self.active_folder

    def set_active_folder(self, folder_name: str) -> bool:
        """
        Set active folder. Returns True if it exists, False otherwise.
        """
        folder_path = self.memory_dir / folder_name
        if folder_path.exists() and folder_path.is_dir():
            self.active_folder = folder_name
            return True
        return False

    def create_folder(self, folder_name: str) -> bool:
        """
        Create a new folder with all necessary files.
        Returns True if created, False if already exists.
        """
        folder_path = self.memory_dir / folder_name
        if folder_path.exists():
            return False

        folder_path.mkdir(parents=True, exist_ok=True)

        # Copy templates to new folder
        for template_file in TEMPLATES_DIR.iterdir():
            if template_file.name in self.FOLDER_FILES:
                dest = folder_path / template_file.name
                self._copy_template(template_file, dest)

        return True

    def folder_exists(self, folder_name: str) -> bool:
        """Check if a folder exists."""
        return (self.memory_dir / folder_name).exists()

    # ─── Path helpers ─────────────────────────────────────────────────────

    def _get_file_path(self, filename: str, folder: str | None = None) -> Path:
        """
        Return full path for a file.
        If folder is None, uses active_folder.
        """
        if folder is None:
            folder = self.active_folder
        if folder is None:
            raise ValueError("No active folder and no folder specified.")
        return self.memory_dir / folder / filename

    def _get_global_file_path(self, filename: str) -> Path:
        """Return path for a file in _global/."""
        return self.global_dir / filename

    # ─── Low-level JSON ops ─────────────────────────────────────────────────

    def load(self, filename: str, folder: str | None = None) -> Any:
        """Load a JSON file from specified or active folder."""
        path = self._get_file_path(filename, folder)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_global(self, filename: str) -> Any:
        """Load a JSON file from _global/."""
        path = self._get_global_file_path(filename)
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, filename: str, data: Any, folder: str | None = None) -> None:
        """Save data to a JSON file in specified or active folder."""
        path = self._get_file_path(filename, folder)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_global(self, filename: str, data: Any) -> None:
        """Save data to a JSON file in _global/."""
        path = self._get_global_file_path(filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def append(self, filename: str, item: dict, folder: str | None = None) -> str:
        """
        Append an item to a JSON array (with auto-id and timestamp).
        Returns the generated ID.
        """
        data = self.load(filename, folder)
        if data is None:
            data = []

        item = dict(item)  # copy
        base_name = filename.replace(".json", "")
        item["id"] = f"{base_name}_{len(data) + 1}_{datetime.now().strftime('%H%M%S')}"
        item["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if folder:
            item["_folder"] = folder

        data.append(item)
        self.save(filename, data, folder)
        return item["id"]

    def append_to_global(self, filename: str, item: dict) -> str:
        """Append an item to a file in _global/."""
        data = self.load_global(filename) or []
        item = dict(item)
        item["id"] = f"global_{len(data) + 1}"
        item["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data.append(item)
        self.save_global(filename, data)
        return item["id"]

    # ─── Profile (_global/profile.json) ──────────────────────────────────────

    def get_profile(self) -> dict:
        """Return global user profile."""
        profile = self.load_global("profile.json")
        return profile if profile else {}

    def update_profile(self, key: str, value: Any) -> None:
        """Update a single key in global profile."""
        profile = self.get_profile()
        profile[key] = value
        self.save_global("profile.json", profile)

    # ─── Identities per folder (_global/identitati.json) ───────────────────

    def get_identities(self) -> list[dict]:
        """Return all identities per folder."""
        return self.load_global("identitati.json") or []

    def add_identity(self, folder: str, identity_data: dict) -> None:
        """Add an identity for a folder."""
        identities = self.get_identities()
        for ident in identities:
            if ident.get("folder") == folder:
                ident.update(identity_data)
                ident["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        else:
            identities.append({
                "folder": folder,
                **identity_data,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        self.save_global("identitati.json", identities)

    # ─── Cross-folder search ─────────────────────────────────────────────────

    def search_all_folders(self, keyword: str) -> dict[str, list[dict]]:
        """
        Search a keyword in all folders and _global/.
        Returns dict with folder -> list of results.
        """
        keyword_lower = keyword.lower()
        results: dict[str, list[dict]] = {}

        # Search in _global/
        global_results = []
        for filename in ["profile.json", "identitati.json"]:
            data = self.load_global(filename)
            if data:
                text = json.dumps(data, ensure_ascii=False).lower()
                if keyword_lower in text:
                    global_results.append({"source": f"_global/{filename}", "data": data})
        if global_results:
            results["_global"] = global_results

        # Search in each folder
        for folder_name in self.get_all_folders():
            folder_results = []
            for filename in self.FOLDER_FILES:
                items = self.load(filename, folder_name) or []
                tip = filename.replace(".json", "")
                for item in items:
                    text = json.dumps(item, ensure_ascii=False).lower()
                    if keyword_lower in text:
                        folder_results.append({
                            "source": f"{folder_name}/{filename}",
                            "data": item,
                        })
            if folder_results:
                results[folder_name] = folder_results

        return results

    def get_all_patterns(self) -> dict[str, dict]:
        """
        Return patterns from ALL folders.
        Returns dict with folder -> pattern data.
        """
        all_patterns: dict[str, dict] = {}
        for folder_name in self.get_all_folders():
            patterns = self.load("patterns.json", folder_name)
            if patterns:
                all_patterns[folder_name] = patterns
        return all_patterns

    def get_all_discoveries(self) -> dict[str, list[dict]]:
        """Return discoveries from ALL folders."""
        all_discoveries: dict[str, list[dict]] = {}
        for folder_name in self.get_all_folders():
            discoveries = self.load("discoveries.json", folder_name)
            if discoveries:
                all_discoveries[folder_name] = discoveries
        return all_discoveries

    def get_all_learning(self) -> dict[str, list[dict]]:
        """Return learnings from ALL folders."""
        all_learning: dict[str, list[dict]] = {}
        for folder_name in self.get_all_folders():
            learning = self.load("learning.json", folder_name)
            if learning:
                all_learning[folder_name] = learning
        return all_learning

    # ─── Connections ─────────────────────────────────────────────────────────

    def find_connections(self, person: str) -> list[dict]:
        """
        Search all mentions of a person across all folders.
        Returns array of connections with source, date, context.
        """
        person_lower = person.lower()
        results = []

        for folder_name in self.get_all_folders():
            for filename in self.FOLDER_FILES:
                items = self.load(filename, folder_name) or []
                tip = filename.replace(".json", "")
                for item in items:
                    text = json.dumps(item, ensure_ascii=False).lower()
                    if person_lower in text:
                        context = item.get("about", item.get("description", ""))[:100]
                        results.append({
                            "type": tip,
                            "date": item.get("date", ""),
                            "context": context,
                            "source": item.get("with_who", ""),
                            "folder": folder_name,
                        })

        return sorted(results, key=lambda x: x["data"], reverse=True)

    # ─── Item move ───────────────────────────────────────────────────────────

    def move_item(self, item_id: str, from_folder: str, to_folder: str, filename: str) -> bool:
        """
        Move an item from one folder to another.
        Search by ID and move.
        """
        items = self.load(filename, from_folder) or []
        item_index = None
        item_to_move = None

        for i, item in enumerate(items):
            if item.get("id") == item_id:
                item_index = i
                item_to_move = item
                break

        if item_index is None or item_to_move is None:
            return False

        items.pop(item_index)
        self.save(filename, items, from_folder)

        item_to_move["_folder"] = to_folder
        self.append(filename, item_to_move, to_folder)

        return True

    # ─── Stats ───────────────────────────────────────────────────────────────

    def get_stats(self) -> dict[str, dict[str, int]]:
        """
        Return statistics for all folders.
        Format: {folder: {category: count}}
        """
        stats: dict[str, dict[str, int]] = {}

        for folder_name in self.get_all_folders():
            folder_stats = {}
            for filename in self.FOLDER_FILES:
                data = self.load(filename, folder_name)
                folder_stats[filename.replace(".json", "")] = len(data) if data else 0
            stats[folder_name] = folder_stats

        return stats

    # ─── Profile fields by context ───────────────────────────────────────────

    def get_context_profile(self, folder: str) -> dict | None:
        """Return context profile for a specific folder."""
        identities = self.get_identities()
        for ident in identities:
            if ident.get("folder") == folder:
                return ident
        return None
