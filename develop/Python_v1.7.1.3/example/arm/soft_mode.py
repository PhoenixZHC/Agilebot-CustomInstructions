#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import SoftModeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置机器人当前的软状态为手动限速模式
ret = arm.set_soft_mode(SoftModeEnum.MANUAL_LIMIT)
# 检查是否成功
assert ret == StatusCodeEnum.OK
# 打印结果
print(f"机器人软状态设定结果：{ret.errmsg}")

# 获取机器人当前的软状态
state, ret = arm.get_soft_mode()
# 检查是否成功
assert ret == StatusCodeEnum.OK
# 打印结果
print(f"机器人当前的软状态：{state.name}")

# 断开捷勃特机器人连接
arm.disconnect()