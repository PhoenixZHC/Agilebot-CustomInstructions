#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 全局参数设置示例 / Example of system parameter setting
"""
from Agilebot import Arm, StatusCodeEnum, TCSType

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 设置机器人各参数
# [EN] Set robot parameters
ret = arm.motion.set_OVC(0.7)
if ret == StatusCodeEnum.OK:
    print("设置全局速度比率成功 / Set global velocity ratio successful")
else:
    print(f"设置全局速度比率失败，错误代码 / Set global velocity ratio failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

ret = arm.motion.set_OAC(0.7)
if ret == StatusCodeEnum.OK:
    print("设置全局加速度比率成功 / Set global acceleration ratio successful")
else:
    print(f"设置全局加速度比率失败，错误代码 / Set global acceleration ratio failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

ret = arm.motion.set_TCS(TCSType.TOOL)
if ret == StatusCodeEnum.OK:
    print("设置示教坐标系类型成功 / Set teaching coordinate system type successful")
else:
    print(f"设置示教坐标系类型失败，错误代码 / Set teaching coordinate system type failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

ret = arm.motion.set_UF(0)
if ret == StatusCodeEnum.OK:
    print("设置用户坐标系成功 / Set user coordinate system successful")
else:
    print(f"设置用户坐标系失败，错误代码 / Set user coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

ret = arm.motion.set_TF(0)
if ret == StatusCodeEnum.OK:
    print("设置工具坐标系成功 / Set tool coordinate system successful")
else:
    print(f"设置工具坐标系失败，错误代码 / Set tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
