#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 插件使用示例 / Example of extension usage
"""
from Agilebot import Arm, Extension, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connection successful")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

res, ret = arm.extension.get("MathService")
if ret == StatusCodeEnum.OK:
    print("获取插件信息成功 / Get extension information successfully")
    print(f"插件信息 / Extension information: {res}")
else:
    print(f"获取插件信息失败，错误代码 / Get extension information failed, error code: {ret.errmsg}")

ret = arm.extension.toggle("MathService")
if ret == StatusCodeEnum.OK:
    print("切换插件状态成功 / Toggle extension status successfully")
else:
    print(f"切换插件状态失败，错误代码 / Toggle extension status failed, error code: {ret.errmsg}")

res, ret = arm.extension.call_service("MathService", "add", dict([["a", 1], ["b", 2]]))
if ret == StatusCodeEnum.OK:
    print("调用插件服务成功 / Call extension service successfully")
    print(f"调用插件服务结果 / Call extension service result: {res}")
else:
    print(f"调用插件服务失败，错误代码 / Call extension service failed, error code: {ret.errmsg}")
