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

# 获取机器人各参数并打印
res, ret = arm.motion.get_OVC()
assert ret == StatusCodeEnum.OK
print(f"全局速度比率：{res}")

res, ret = arm.motion.get_OAC()
assert ret == StatusCodeEnum.OK
print(f"全局加速度比率：{res}")

res, ret = arm.motion.get_TCS()
assert ret == StatusCodeEnum.OK
print(f"示教坐标系类型：{TCSType(res).name}")

res, ret = arm.motion.get_UF()
assert ret == StatusCodeEnum.OK
print(f"用户坐标系：{res}")

res, ret = arm.motion.get_TF()
assert ret == StatusCodeEnum.OK
print(f"工具坐标系：{res}")

# 断开捷勃特机器人连接
arm.disconnect()
