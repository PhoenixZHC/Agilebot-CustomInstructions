#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 更新负载使用示例 / Example of updating the load
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to Agilebot robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取负载
# [EN] Get payload
payload_info, ret_code = arm.motion.payload.get_payload_by_id(6)
payload_info.comment = "Test"
payload_info.weight = 10
payload_info.mass_center.x = -100
payload_info.mass_center.y = 10
payload_info.mass_center.z = 10
payload_info.inertia_moment.lx = 10
payload_info.inertia_moment.ly = 10
payload_info.inertia_moment.lz = 10

# [ZH] 更新负载
# [EN] Update payload
ret = arm.motion.payload.update_payload(payload_info)
if ret == StatusCodeEnum.OK:
    print("更新负载成功 / Update payload successful")
else:
    print(f"更新负载失败，错误代码 / Update payload failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(
    f"负载ID / Payload ID: {payload_info.id}\n"
    f"负载质量 / Payload mass: {payload_info.weight}\n"
    f"负载质心 / Payload mass center: {payload_info.mass_center.x}, {payload_info.mass_center.y}, {payload_info.mass_center.z}\n"
    f"负载转动惯量 / Payload inertia moment: {payload_info.inertia_moment.lx}, {payload_info.inertia_moment.ly}, {payload_info.inertia_moment.lz}\n"
    f"负载注释 / Payload comment: {payload_info.comment}\n"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
