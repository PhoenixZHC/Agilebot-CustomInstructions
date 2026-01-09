#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 拖动示教使用示例 / example of drag teaching usage 
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to Agilebot robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 进入拖动示教
# [EN] Enter drag teaching mode
ret = arm.motion.enable_drag(True)
if ret == StatusCodeEnum.OK:
    print("进入拖动示教成功 / Enter drag teaching successful")
else:
    print(f"进入拖动示教失败，错误代码 / Enter drag teaching failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 退出拖动示教
# [EN] Exit drag teaching mode
ret = arm.motion.enable_drag(False)
if ret == StatusCodeEnum.OK:
    print("退出拖动示教成功 / Exit drag teaching successful")
else:
    print(f"退出拖动示教失败，错误代码 / Exit drag teaching failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
