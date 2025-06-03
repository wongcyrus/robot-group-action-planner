from asyncio import sleep
from load_spreadsheet import get_google_spreadsheet

from action import RobotAction
import time

if __name__ == "__main__":
    result = get_google_spreadsheet("1JmjO4Yidu2pLtJxEuu4mYPX14AYmEj0przne75JBg6Y")

    robot_1 = RobotAction("192.168.1.2")
    robot_2 = RobotAction("192.168.1.3")
    robot_3 = RobotAction("192.168.1.4")
    robot_4 = RobotAction("192.168.1.5")
    robot_5 = RobotAction("192.168.1.6")
    robot_6 = RobotAction("192.168.1.7")

    for row in result:
        print(row)
        time_value = row["Time"]
        robot_1_action = row["Robot_1"]
        robot_2_action = row["Robot_2"]
        robot_3_action = row["Robot_3"]
        robot_4_action = row["Robot_4"]
        robot_5_action = row["Robot_5"]
        robot_6_action = row["Robot_6"]

        print(f"Time: {time_value}")
        robot_1.run_action(robot_1_action)
        robot_2.run_action(robot_2_action)
        robot_3.run_action(robot_3_action)
        robot_4.run_action(robot_4_action)
        robot_5.run_action(robot_5_action)
        robot_6.run_action(robot_6_action)
        time.sleep(float(time_value))

    print(result)