#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 实时位置控制模式使用示例 / Example of the real-time location control mode usage
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

# [ZH] 设置udp反馈参数
# [EN] Set UDP feedback parameters
ret = arm.motion.set_udp_feedback_params(True, "10.27.1.254", 20, 1, [0, 1, 2])
if ret == StatusCodeEnum.OK:
    print("设置UDP反馈参数成功 / Set UDP feedback parameters successful")
else:
    print(f"设置UDP反馈参数失败，错误代码 / Set UDP feedback parameters failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 进入实时位置控制模式
# [EN] Enter real-time position control mode
ret = arm.motion.enter_position_control()
if ret == StatusCodeEnum.OK:
    print("进入实时位置控制模式成功 / Enter real-time position control mode successful")
else:
    print(f"进入实时位置控制模式失败，错误代码 / Enter real-time position control mode failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 在此插入发送UDP数据控制机器人代码
# [EN] Insert UDP data sending code to control robot here

# [ZH] 退出实时位置控制模式
# [EN] Exit real-time position control mode
ret = arm.motion.exit_position_control()
if ret == StatusCodeEnum.OK:
    print("退出实时位置控制模式成功 / Exit real-time position control mode successful")
else:
    print(f"退出实时位置控制模式失败，错误代码 / Exit real-time position control mode failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
