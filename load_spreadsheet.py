import csv
from io import StringIO
import requests


def get_google_spreadsheet(spreadsheet_id):
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv"
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        csv_str = response.content.decode("utf-8")
        f = StringIO(csv_str)
        spreadsheet_data = []
        reader = csv.reader(f, delimiter=",")
        next(reader, None)  # Skip the header row
        for row in reader:
            if len(row) < 4:
                continue
            time, robot_1, robot_2, robot_3,robot_4,robot_5,robot_6 = row[:7]
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
    return None