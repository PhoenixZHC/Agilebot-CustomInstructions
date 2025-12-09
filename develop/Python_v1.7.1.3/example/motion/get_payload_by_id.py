#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.common.const import const

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取负载
res, ret = arm.motion.payload.get_payload_by_id(1)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
        f"负载ID:{res.id}\n"
        f"负载质量:{res.m_load}\n"
        f"负载注释:{res.comment}\n"
    )

# 断开捷勃特机器人连接
arm.disconnect()
