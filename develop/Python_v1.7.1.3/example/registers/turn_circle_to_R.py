#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum


# 初始化捷勃特机器人
arm = Arm()

# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
assert ret == StatusCodeEnum.OK

# 需要写入R寄存器的回转数（示例：-1 / 1 / 0）
turn_circle_values = [-1, 1, 0]

# 起始R寄存器编号，turn_circle_values[0] -> R[start_r_id]
start_r_id = 100

# 逐个写入R寄存器
for idx, value in enumerate(turn_circle_values):
    r_id = start_r_id + idx
    ret = arm.register.write_R(r_id, int(value))
    assert ret == StatusCodeEnum.OK

# 回读并打印结果
for idx in range(len(turn_circle_values)):
    r_id = start_r_id + idx
    res, ret = arm.register.read_R(r_id)
    assert ret == StatusCodeEnum.OK
    print(f"R[{r_id}] = {res}")

# 断开捷勃特机器人连接
arm.disconnect()

