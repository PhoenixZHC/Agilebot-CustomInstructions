#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 拖动设置使用示例 / Example of drag Settings usage
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

# [ZH] 获取当前轴锁定状态
# [EN] Get current axis lock status
drag_status, ret = arm.motion.get_drag_set()
if ret == StatusCodeEnum.OK:
    print("获取拖动设置成功 / Get drag set successful")
else:
    print(f"获取拖动设置失败，错误代码 / Get drag set failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(
    f"当前X轴拖动状态 / Current X axis drag status: {drag_status.cart_status.x}\n"
    f"当前Y轴拖动状态 / Current Y axis drag status: {drag_status.cart_status.y}\n"
    f"当前Z轴拖动状态 / Current Z axis drag status: {drag_status.cart_status.z}"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
