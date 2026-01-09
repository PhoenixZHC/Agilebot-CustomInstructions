#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 添加负载使用示例 / Example of Add load usage
"""
from Agilebot import Arm, PayloadInfo, StatusCodeEnum

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

# [ZH] 初始化负载
# [EN] Initialize payload
new_payload = PayloadInfo()
new_payload.id = 6
new_payload.comment = "Test"
new_payload.weight = 5
new_payload.mass_center.x = -151
new_payload.mass_center.y = 1.0
new_payload.mass_center.z = 75
new_payload.inertia_moment.lx = 0.11
new_payload.inertia_moment.ly = 0.61
new_payload.inertia_moment.lz = 0.54

# [ZH] 添加负载
# [EN] Add payload
ret = arm.motion.payload.add_payload(new_payload)
if ret == StatusCodeEnum.OK:
    print("添加负载成功 / Add payload successful")
else:
    print(f"添加负载失败，错误代码 / Add payload failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
