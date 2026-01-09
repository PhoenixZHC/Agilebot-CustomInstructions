#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Arm类下的机器人软状态获取示例 / Example of obtaining the soft state of a robot
"""
from Agilebot import Arm, SoftModeEnum, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 设置机器人当前的软状态为手动限速模式
# [EN] Set the robot's current soft state to manual limit mode
ret = arm.set_soft_mode(SoftModeEnum.MANUAL_LIMIT)
# [ZH] 检查是否成功
# [EN] Check if successful
if ret == StatusCodeEnum.OK:
    print("设置机器人当前的软状态为手动限速模式成功 / Set the robot's current soft state to manual limit mode successfully")
else:
    print(
        f"设置机器人当前的软状态为手动限速模式失败，错误代码 / Set the robot's current soft state to manual limit mode failed, error code: {ret.errmsg}"
    )
    arm.disconnect()
    exit(1)

# [ZH] 获取机器人当前的软状态
# [EN] Get the robot's current soft state
state, ret = arm.get_soft_mode()
# [ZH] 检查是否成功
# [EN] Check if successful
if ret == StatusCodeEnum.OK:
    print("获取机器人当前的软状态成功 / Get the robot's current soft state successfully")
    print(f"机器人当前的软状态 / Robot current soft state: {state.name}")
else:
    print(f"获取机器人当前的软状态失败，错误代码 / Get the robot's current soft state failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
