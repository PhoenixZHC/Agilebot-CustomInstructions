#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取当前轴锁定状态
drag_status, ret = arm.motion.get_drag_set()
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"当前X轴拖动状态：{drag_status.cart_status.x}\n"
    f"当前Y轴拖动状态：{drag_status.cart_status.y}\n"
    f"当前Z轴拖动状态：{drag_status.cart_status.z}"
    )

# 断开捷勃特机器人连接
arm.disconnect()
