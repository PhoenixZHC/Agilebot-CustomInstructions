#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 所有负载获取示例 / Example of all load acquisition 
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化Arm类
# [EN] Initialize Arm class
arm = Arm()
# [ZH] 连接控制器
# [EN] Connect to controller
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取所有负载
# [EN] Get all payloads
res, ret = arm.motion.payload.get_all_payload()
if ret == StatusCodeEnum.OK:
    print("获取所有负载成功 / Get all payloads successful")
else:
    print(f"获取所有负载失败，错误代码 / Get all payloads failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
for payload in res:
    print(f"负载ID / Payload ID: {payload[0]}\n" f"负载注释 / Payload comment: {payload[1]}\n")

# [ZH] 结束后断开机器人连接
# [EN] Disconnect from robot after completion
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
