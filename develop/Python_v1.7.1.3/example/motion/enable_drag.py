#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 进入拖动示教
ret = arm.motion.enable_drag(True)
assert ret == StatusCodeEnum.OK

# 打印结果
print("开始拖动示教")

# 退出拖动示教
ret = arm.motion.enable_drag(False)
assert ret == StatusCodeEnum.OK

# 打印结果
print("退出拖动示教")

# 断开捷勃特机器人连接
arm.disconnect()
