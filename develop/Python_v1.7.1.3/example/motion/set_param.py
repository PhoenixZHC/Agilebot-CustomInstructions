#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import TCSType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置机器人各参数
ret = arm.motion.set_OVC(0.7)
assert ret == StatusCodeEnum.OK

ret = arm.motion.set_OAC(0.7)
assert ret == StatusCodeEnum.OK

ret = arm.motion.set_TCS(TCSType.TOOL)
assert ret == StatusCodeEnum.OK

ret = arm.motion.set_UF(0)
assert ret == StatusCodeEnum.OK

ret = arm.motion.set_TF(0)
assert ret == StatusCodeEnum.OK

print(f"参数设置成功")

# 断开捷勃特机器人连接
arm.disconnect()
