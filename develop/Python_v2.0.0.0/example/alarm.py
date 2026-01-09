#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 告警功能使用示例 / Example of using the alarm function
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the robot
arm = Arm()

# [ZH] 连接捷勃特机器人
# [EN] Connect to the robot
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取所有的活动的报警
# [EN] Get all active alarms
alarms, ret = arm.alarm.get_all_active_alarms()
if ret == StatusCodeEnum.OK:
    print("获取报警信息成功 / Get alarm information successfully")
    for alarm in alarms:
        print(alarm)
else:
    print(f"获取报警信息失败，错误代码 / Failed to get alarm information, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取所有的活动的报警
# [EN] Get all active alarms
alarm, ret = arm.alarm.get_top_alarm()
if ret == StatusCodeEnum.OK:
    print("获取报警信息成功 / Get alarm information successfully")
    for alarm in alarm:
        print(alarm)
else:
    print(f"获取报警信息失败，错误代码 / Failed to get alarm information, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 重置报警
# [EN] Reset alarms
ret = arm.alarm.reset()
if ret == StatusCodeEnum.OK:
    print("报警重置成功 / Alarm reset successfully")
else:
    print(f"报警重置失败，错误代码 / Alarm reset failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
