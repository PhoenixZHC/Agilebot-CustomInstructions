#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 全局参数获取示例 / Example of system parameter acquisition
"""
from Agilebot import Arm, StatusCodeEnum, TCSType

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

# [ZH] 获取机器人各参数并打印
# [EN] Get robot parameters and print
res, ret = arm.motion.get_OVC()
if ret == StatusCodeEnum.OK:
    print("获取全局速度比率成功 / Get global velocity ratio successful")
else:
    print(f"获取全局速度比率失败，错误代码 / Get global velocity ratio failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
print(f"全局速度比率 / Global velocity ratio: {res}")

res, ret = arm.motion.get_OAC()
if ret == StatusCodeEnum.OK:
    print("获取全局加速度比率成功 / Get global acceleration ratio successful")
else:
    print(f"获取全局加速度比率失败，错误代码 / Get global acceleration ratio failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
print(f"全局加速度比率 / Global acceleration ratio: {res}")

res, ret = arm.motion.get_TCS()
if ret == StatusCodeEnum.OK:
    print("获取示教坐标系类型成功 / Get teaching coordinate system type successful")
else:
    print(f"获取示教坐标系类型失败，错误代码 / Get teaching coordinate system type failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
print(f"示教坐标系类型 / Teaching coordinate system type: {TCSType(res).name}")

res, ret = arm.motion.get_UF()
if ret == StatusCodeEnum.OK:
    print("获取用户坐标系成功 / Get user coordinate system successful")
else:
    print(f"获取用户坐标系失败，错误代码 / Get user coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
print(f"用户坐标系 / User coordinate system: {res}")

res, ret = arm.motion.get_TF()
if ret == StatusCodeEnum.OK:
    print("获取工具坐标系成功 / Get tool coordinate system successful")
else:
    print(f"获取工具坐标系失败，错误代码 / Get tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
print(f"工具坐标系 / Tool coordinate system: {res}")

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
