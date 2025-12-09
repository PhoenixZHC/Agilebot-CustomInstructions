#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 读取MH寄存器
res, ret = arm.register.read_MH(1)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"MH寄存器：{res}"
    )

# 写入MH寄存器
assert arm.register.write_MH(1, 16) == StatusCodeEnum.OK

# 读取MI寄存器
res, ret = arm.register.read_MI(1)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"MI寄存器：{res}"
    )

# 写入MI寄存器
assert arm.register.write_MI(1, 18) == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
