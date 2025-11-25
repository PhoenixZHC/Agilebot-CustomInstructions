#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 删除指定ID负载
ret = arm.motion.payload.delete_payload(6)
assert ret == StatusCodeEnum.OK

# 打印结果
print(f"删除负载6成功")

# 断开捷勃特机器人连接
arm.disconnect()
