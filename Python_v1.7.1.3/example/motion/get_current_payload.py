#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取当前激活负载
current_payload_id, ret = arm.motion.payload.get_current_payload()
assert ret == StatusCodeEnum.OK

# 打印结果
print(f"当前激活负载ID为：{current_payload_id}")

# 断开捷勃特机器人连接
arm.disconnect()
