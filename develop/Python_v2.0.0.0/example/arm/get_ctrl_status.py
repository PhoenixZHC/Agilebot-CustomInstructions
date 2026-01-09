#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Arm类下的获取运动控制器运行状态示例 / Example of the operating status of the controller
"""
from Agilebot import Arm, StatusCodeEnum

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

# [ZH] 获取运动控制器运行状态
# [EN] Get the controller running status
state, ret = arm.get_ctrl_status()
# [ZH] 检查是否成功
# [EN] Check if successful
if ret == StatusCodeEnum.OK:
    print("获取运动控制器运行状态成功 / Get controller running status successful")
    print(f"运动控制器运行状态 / Controller running status: {state.msg}")
else:
    print(f"获取运动控制器运行状态失败，错误代码 / Get controller running status failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
