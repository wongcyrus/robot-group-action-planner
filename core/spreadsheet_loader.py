import csv
from io import StringIO
from typing import Dict, List, Optional

import requests

from config.settings import AppConfig
from constant import ACTION_DETAILS_SPREADSHEET_ID, ACTION_SEQUENCE_SPREADSHEET_ID
from core.cache_manager import cache_manager


class SpreadsheetLoader:
    """Class for loading and parsing Google Spreadsheet data."""

    # Class-level cache for action details data - shared across all instances
    _action_details_cache: Optional[List[Dict[str, str]]] = None

    # Class-level cache for macro data - shared across all instances
    _macro_cache: Optional[List[Dict[str, str]]] = None

    # Class-level cache for robot actions data by song name
    _robot_actions_cache: Dict[str, List[Dict[str, str]]] = {}

    def __init__(
        self,
        dance: str,
    ):

        self.robot_actions_spreadsheet_id = ACTION_SEQUENCE_SPREADSHEET_ID
        self.action_details_spreadsheet_id = ACTION_DETAILS_SPREADSHEET_ID
        self.dance = dance
        self.robot_actions_data = (
            self._load_robot_actions() if self.robot_actions_spreadsheet_id else []
        )
        self.action_details_data, self.macro_data = (
            self._load_action_details()
            if self.action_details_spreadsheet_id
            else ([], [])
        )

    def _fetch_spreadsheet_data(
        self, spreadsheet_id: str, sheet_name: Optional[str] = None
    ) -> Optional[StringIO]:
        """Fetch raw data from Google Spreadsheet."""
        if sheet_name is None:
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
        else:
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        print(f"Fetching spreadsheet data from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            csv_str = response.content.decode("utf-8")
            return StringIO(csv_str)
        except (requests.RequestException, UnicodeDecodeError) as e:
            print(f"Error fetching spreadsheet: {e}")
        return None

    def _load_csv_data(self, f: StringIO, columns: List[str]) -> List[Dict[str, str]]:
        """Load CSV data into a list of dictionaries with given columns."""
        spreadsheet_data = []
        reader = csv.reader(f, delimiter=",")
        next(reader, None)  # Skip header
        for row in reader:
            if not row or not row[0]:
                continue
            entry = {col: row[idx] for idx, col in enumerate(columns) if idx < len(row)}
            spreadsheet_data.append(entry)
        return spreadsheet_data

    def _load_robot_actions(self) -> List[Dict[str, str]]:
        # Create cache key for this song's robot actions
        cache_key = f"robot_actions_{self.dance}_{self.robot_actions_spreadsheet_id}"

        # Try to get from file cache first
        cached_data = cache_manager.get_cache(cache_key)
        if cached_data is not None:
            print(f"Using file cached robot actions data for song: {self.dance}")
            # Also update in-memory cache for consistency
            SpreadsheetLoader._robot_actions_cache[self.dance] = cached_data
            return cached_data

        # Check if we have in-memory cached data for this song
        if self.dance in SpreadsheetLoader._robot_actions_cache:
            print(f"Using in-memory cached robot actions data for song: {self.dance}")
            return SpreadsheetLoader._robot_actions_cache[self.dance]

        # Fetch data if not cached
        f = self._fetch_spreadsheet_data(self.robot_actions_spreadsheet_id, self.dance)
        if not f:
            print("Failed to fetch robot actions spreadsheet data.")
            return []

        # Generate columns dynamically based on IP configuration
        columns = self._generate_robot_columns()
        data = self._load_csv_data(f, columns)

        # Cache the data both in-memory and file
        SpreadsheetLoader._robot_actions_cache[self.dance] = data
        cache_manager.set_cache(cache_key, data)
        print(f"Robot actions data cached (memory + file) for song: {self.dance}")
        return data

    def _generate_robot_columns(self) -> List[str]:
        """Generate robot column names based on IP configuration from settings."""
        config = AppConfig.from_constants()
        columns = ["Time"]

        # Add humanoid columns based on configured IPs
        for i in range(len(config.robots.ips)):
            columns.append(f"Humanoid_{i+1}")

        # Add drone columns based on configured IPs
        drone_ips = (
            config.drones.real_hosts
            if not config.drones.simulator_mode
            else [config.drones.simulator_ip]
        )
        for i in range(len(drone_ips)):
            columns.append(f"Drone_{i+1}")

        # Add dog columns based on configured IPs
        for i in range(len(config.dogs.ips)):
            columns.append(f"Dog_{i+1}")

        return columns

    def _load_action_details(self) -> tuple:
        # Create cache keys
        action_details_cache_key = (
            f"action_details_{self.action_details_spreadsheet_id}"
        )
        macro_cache_key = f"macro_{self.action_details_spreadsheet_id}"

        # Try to get from file cache first
        cached_action_details = cache_manager.get_cache(action_details_cache_key)
        cached_macro = cache_manager.get_cache(macro_cache_key)

        if cached_action_details is not None and cached_macro is not None:
            print("Using file cached action details and macro data.")
            # Also update in-memory cache for consistency
            SpreadsheetLoader._action_details_cache = cached_action_details
            SpreadsheetLoader._macro_cache = cached_macro
            return cached_action_details, cached_macro

        # Check if we have in-memory cached data
        if (
            SpreadsheetLoader._action_details_cache is not None
            and SpreadsheetLoader._macro_cache is not None
        ):
            print("Using in-memory cached action details and macro data.")
            return (
                SpreadsheetLoader._action_details_cache,
                SpreadsheetLoader._macro_cache,
            )

        # Fetch action details data if not cached
        f = self._fetch_spreadsheet_data(self.action_details_spreadsheet_id, "Robot")
        if not f:
            print("Failed to fetch action details spreadsheet data.")
            return [], []
        columns = ["Code", "Name", "Time", "Repeat_Time", "Remark", "Link"]
        action_details_data = self._load_csv_data(f, columns)

        # Fetch macro data if not cached
        f = self._fetch_spreadsheet_data(self.action_details_spreadsheet_id, "Macro")
        if not f:
            print("Failed to fetch macro spreadsheet data.")
            return action_details_data, []
        columns = ["Alias", "Actions"]
        macro_data = self._load_csv_data(f, columns)

        # Cache the data both in-memory and file
        SpreadsheetLoader._action_details_cache = action_details_data
        SpreadsheetLoader._macro_cache = macro_data
        cache_manager.set_cache(action_details_cache_key, action_details_data)
        cache_manager.set_cache(macro_cache_key, macro_data)
        print("Action details and macro data cached (memory + file).")
        return action_details_data, macro_data

    @classmethod
    def clear_action_details_cache(cls) -> None:
        """Clear the cached action details and macro data."""
        cls._action_details_cache = None
        cls._macro_cache = None
        # Clear file cache
        action_details_cache_key = f"action_details_{ACTION_DETAILS_SPREADSHEET_ID}"
        macro_cache_key = f"macro_{ACTION_DETAILS_SPREADSHEET_ID}"
        cache_manager.clear_cache(action_details_cache_key)
        cache_manager.clear_cache(macro_cache_key)
        print("Action details and macro cache cleared (memory + file).")

    @classmethod
    def clear_robot_actions_cache(cls, song_name: Optional[str] = None) -> None:
        """
        Clear the cached robot actions data.

        Args:
            song_name: If provided, clears cache only for this song.
                      If None, clears all robot actions cache.
        """
        if song_name:
            if song_name in cls._robot_actions_cache:
                del cls._robot_actions_cache[song_name]
            # Clear file cache for specific song
            cache_key = f"robot_actions_{song_name}_{ACTION_SEQUENCE_SPREADSHEET_ID}"
            cache_manager.clear_cache(cache_key)
            print(f"Robot actions cache cleared (memory + file) for song: {song_name}")
        else:
            cls._robot_actions_cache.clear()
            # Clear all robot actions file caches - this is more complex
            # For now, we'll clear all cache files
            cache_manager.clear_cache()
            print("All robot actions cache cleared (memory + file).")

    @classmethod
    def clear_all_caches(cls) -> None:
        """Clear all cached data."""
        cls.clear_action_details_cache()
        cls.clear_robot_actions_cache()
        print("All caches cleared (memory + file).")

    def get_action_details(self):
        return self.action_details_data

    def get_macro_data(self):
        return self.macro_data

    def get_macro_aliases(self) -> Dict[str, str]:
        """Get a mapping of macro aliases to their action sequences."""
        if not self.macro_data:
            return {}
        macro_aliases = {}
        for macro in self.macro_data:
            alias = macro.get("Alias")
            actions = macro.get("Actions")
            if alias and actions:
                macro_aliases[alias] = actions
        return macro_aliases

    def get_action_name_to_time(self) -> Dict[str, float]:
        """Get a mapping of action names to their time values as floats."""
        if not self.action_details_data:
            raise ValueError("No action details data loaded.")
        action_name_to_time = {}
        for action in self.action_details_data:
            name = action.get("Name")
            time_val = action.get("Time")
            if name and time_val:
                try:
                    action_name_to_time[name] = float(time_val)
                except (ValueError, TypeError):
                    continue
        return action_name_to_time

    def get_action_name_to_repeat_time(self) -> Dict[str, int]:
        """Get a mapping of action names to their repeat time values as integers."""
        if not self.action_details_data:
            raise ValueError("No action details data loaded.")
        action_name_to_repeat_time = {}
        for action in self.action_details_data:
            name = action.get("Name")
            repeat_time_val = action.get("Repeat_Time")
            if name and repeat_time_val:
                try:
                    action_name_to_repeat_time[name] = int(repeat_time_val)
                except (ValueError, TypeError):
                    continue
        return action_name_to_repeat_time

    def get_robot_actions(self):
        return self.robot_actions_data
