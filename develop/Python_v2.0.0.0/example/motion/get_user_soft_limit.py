#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 用户软限位设置获取示例 / Example of obtaining the user's soft limit setting
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

# [ZH] 获取当前机器人软限位信息
# [EN] Get current robot soft limit information
res, ret = arm.motion.get_user_soft_limit()
if ret == StatusCodeEnum.OK:
    print("获取用户软限位成功 / Get user soft limit successful")
else:
    print(f"获取用户软限位失败，错误代码 / Get user soft limit failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(f"当前机器人软限位信息 / Current robot soft limit information: {res}")

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
