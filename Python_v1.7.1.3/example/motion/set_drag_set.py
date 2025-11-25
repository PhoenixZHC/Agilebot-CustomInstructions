#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import DragStatus
from Agilebot.IR.A.sdk_types import TCSType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置示教坐标系
arm.motion.set_TCS(TCSType.BASE)
assert ret == StatusCodeEnum.OK

# 设置要锁定的轴
drag_status = DragStatus()
drag_status.cart_status.x = False
drag_status.cart_status.y = False
# 设置连续拖动开关
drag_status.is_continuous_drag = True

# 设置轴锁定状态
ret = arm.motion.set_drag_set(drag_status)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"当前X轴拖动状态：{drag_status.cart_status.x}\n"
    f"当前Y轴拖动状态：{drag_status.cart_status.y}\n"
    f"当前Z轴拖动状态：{drag_status.cart_status.z}"
    )

# 断开捷勃特机器人连接
arm.disconnect()
