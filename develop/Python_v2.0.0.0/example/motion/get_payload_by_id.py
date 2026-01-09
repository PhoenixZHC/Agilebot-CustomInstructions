#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 根据ID获取负载参数示例 / Example of obtaining load parameters based on ID
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
res, ret = arm.motion.payload.get_payload_by_id(6)
if ret == StatusCodeEnum.OK:
    print("获取负载成功 / Get payload successful")
else:
    print(f"获取负载失败，错误代码 / Get payload failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(
    f"负载ID / Payload ID: {res.id}\n"
    f"负载质量 / Payload mass: {res.weight}\n"
    f"负载注释 / Payload comment: {res.comment}\n"
    f"负载质心 / Payload mass center: {res.mass_center.x}, {res.mass_center.y}, {res.mass_center.z}\n"
    f"负载转动惯量 / Payload inertia moment: {res.inertia_moment.lx}, {res.inertia_moment.ly}, {res.inertia_moment.lz}\n"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
