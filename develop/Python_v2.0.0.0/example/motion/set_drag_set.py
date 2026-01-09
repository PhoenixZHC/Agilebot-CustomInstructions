#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 拖动状态设置实例 / Example of dragging status setting
"""
from Agilebot import Arm, DragStatus, StatusCodeEnum, TCSType

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

# [ZH] 设置示教坐标系
# [EN] Set teaching coordinate system
arm.motion.set_TCS(TCSType.BASE)
if ret == StatusCodeEnum.OK:
    print("操作成功 / Operation successful")
else:
    print(f"操作失败，错误代码 / Operation failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 设置要锁定的轴
# [EN] Set axes to be locked
drag_status = DragStatus()
drag_status.cart_status.x = False
drag_status.cart_status.y = False
# [ZH] 设置连续拖动开关
# [EN] Set continuous drag switch
drag_status.is_continuous_drag = True

# [ZH] 设置轴锁定状态
# [EN] Set axis lock status
ret = arm.motion.set_drag_set(drag_status)
if ret == StatusCodeEnum.OK:
    print("设置拖动状态成功 / Set drag status successful")
else:
    print(f"设置拖动状态失败，错误代码 / Set drag status failed, error code: {ret.errmsg}")
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
