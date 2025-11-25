#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取负载
payload_info, ret_code = arm.motion.payload.get_payload_by_id(1)
payload_info.comment = 'Test'.encode('utf-8')

# 更新负载
ret = arm.motion.payload.update_payload(payload_info)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
        f"负载ID:{payload_info.id}\n"
        f"负载质量:{payload_info.m_load}\n"
        f"负载注释:{payload_info.comment}\n"
    )

# 断开捷勃特机器人连接
arm.disconnect()
