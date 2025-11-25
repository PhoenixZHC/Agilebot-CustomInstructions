#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.flyshot import Payload

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 初始化负载
new_payload = Payload()
new_payload.id = 6
new_payload.m_load = 18
new_payload.lcx_load = -151
new_payload.lcy_load = 1.0
new_payload.lcz_load = 75
new_payload.Ixx_load = 0.11
new_payload.Iyy_load = 0.61
new_payload.Izz_load = 0.54
new_payload.comment = 'Test'.encode('utf-8')

# 添加负载
ret = arm.motion.payload.add_payload(new_payload)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
        f"负载ID:{new_payload.id}\n"
        f"负载质量:{new_payload.m_load}\n"
        f"负载注释:{new_payload.comment}\n"
    )

# 断开捷勃特机器人连接
arm.disconnect()
