import csv
from io import StringIO
from typing import Dict, List, Optional

import requests

from constant import (
    ACTION_DETAILS_SPREADSHEET_ID,
    ACTION_SEQUENCE_SPREADSHEET_ID,
    ROBOT_IPS,
)


class SpreadsheetLoader:
    """Class for loading and parsing Google Spreadsheet data."""

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
        self.action_details_data = (
            self._load_action_details() if self.action_details_spreadsheet_id else []
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
        f = self._fetch_spreadsheet_data(self.robot_actions_spreadsheet_id, self.dance)
        if not f:
            print("Failed to fetch robot actions spreadsheet data.")
            return []
        columns = [
            "Time",
            "Robot_1",
            "Robot_2",
            "Robot_3",
            "Robot_4",
            "Robot_5",
            "Robot_6",
        ]
        return self._load_csv_data(f, columns)

    def _load_action_details(self) -> List[Dict[str, str]]:
        f = self._fetch_spreadsheet_data(self.action_details_spreadsheet_id)
        if not f:
            print("Failed to fetch action details spreadsheet data.")
            return []
        columns = ["Code", "Name", "Time", "Repeat_Time", "Remark", "Link"]
        return self._load_csv_data(f, columns)

    def get_action_details(self):
        return self.action_details_data

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
