import csv
from io import StringIO
import requests


class SpreadsheetLoader:
    """Class for loading and parsing Google Spreadsheet data."""
    
    def __init__(self, robot_actions_spreadsheet_id=None, action_details_spreadsheet_id=None):
        """Initialize the SpreadsheetLoader.
        
        Args:
            robot_actions_spreadsheet_id (str, optional): The ID of the Google Spreadsheet containing robot actions.
            action_details_spreadsheet_id (str, optional): The ID of the Google Spreadsheet containing action details.
        """
        self.robot_actions_spreadsheet_id = robot_actions_spreadsheet_id
        self.action_details_spreadsheet_id = action_details_spreadsheet_id
        
        # Pre-load data if spreadsheet IDs are provided
        self.robot_actions_data = None
        self.action_details_data = None
        
        if self.robot_actions_spreadsheet_id:
            self.robot_actions_data = self._load_robot_actions()
            
        if self.action_details_spreadsheet_id:
            self.action_details_data = self._load_action_details()
        
    def _fetch_spreadsheet_data(self, spreadsheet_id):
        """Fetch raw data from Google Spreadsheet.
        
        Args:
            spreadsheet_id (str): The ID of the Google Spreadsheet.
            
        Returns:
            StringIO or None: CSV data as StringIO object or None if request failed.
        """
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                csv_str = response.content.decode("utf-8")
                return StringIO(csv_str)        
        except Exception as e:
            print(f"Error fetching spreadsheet: {e}")
        return None
    
    def _load_robot_actions(self):
        """Load robot action sequence from Google Spreadsheet.
        
        Returns:
            list or None: List of dictionaries containing robot actions or None if failed.
        """
        f = self._fetch_spreadsheet_data(self.robot_actions_spreadsheet_id)
        if not f:
            raise ValueError("Failed to fetch action details spreadsheet data.")
            
        spreadsheet_data = []
        reader = csv.reader(f, delimiter=",")
        next(reader, None)  # Skip the header row
        
        for row in reader:
            time, robot_1, robot_2, robot_3, robot_4, robot_5, robot_6 = row[:7]
            if not time:
                continue
                
            spreadsheet_data.append(
                {
                    "Time": time,
                    "Robot_1": robot_1,
                    "Robot_2": robot_2,
                    "Robot_3": robot_3,
                    "Robot_4": robot_4,
                    "Robot_5": robot_5,
                    "Robot_6": robot_6,
                }
            )
        return spreadsheet_data
        

    
    def _load_action_details(self):
        """Load action details from Google Spreadsheet.
        
        Returns:
            list or None: List of dictionaries containing action details or None if failed.
        """
        f = self._fetch_spreadsheet_data(self.action_details_spreadsheet_id)
        if not f:
            raise ValueError("Failed to fetch action details spreadsheet data.")
            
        spreadsheet_data = []
        reader = csv.reader(f, delimiter=",")
        next(reader, None)  # Skip the header row
        
        for row in reader:                
            code, name, time, repeat_time, remark, link = row[:6]
            if not time:
                continue
                
            spreadsheet_data.append(
                {
                    "Code": code,
                    "Name": name,
                    "Time": time,
                    "Repeat_Time": repeat_time,
                    "Remark": remark,
                    "Link": link,
                }
            )
        return spreadsheet_data
    
    def get_action_details(self):        
        return self.action_details_data
    
    def get_action_name_to_time(self):
        """Get a mapping of action names to their time values."""
        if not self.action_details_data:
            raise ValueError("No action details data loaded.")
        
        action_name_to_time = {}
        for action in self.action_details_data:
            name = action.get("Name")
            time = action.get("Time")
            if name and time:
                action_name_to_time[name] = time
        return action_name_to_time
   
    def get_robot_actions(self):
        return self.robot_actions_data
