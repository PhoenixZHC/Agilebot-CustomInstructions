#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import SignalType, SignalValue

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 读取IO
do_value, ret = arm.signals.read(SignalType.DO, 1)
assert ret == StatusCodeEnum.OK

# 打印结果
print(f"DO 1 状态：{do_value}")

# 写入IO
ret = arm.signals.write(SignalType.DO, 1, SignalValue.ON)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
