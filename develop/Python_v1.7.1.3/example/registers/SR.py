#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 添加SR寄存器
ret = arm.register.write_SR(5, 'pytest')
assert ret == StatusCodeEnum.OK

# 读取SR寄存器
res, ret = arm.register.read_SR(5)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"SR寄存器值：{res}"
    )

# 删除SR寄存器
ret = arm.register.delete_SR(5)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
