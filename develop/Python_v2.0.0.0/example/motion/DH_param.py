#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: DH参数设置使用示例 / Example of DH parameter setting usage
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

# [ZH] 获取DH参数
# [EN] Get DH parameters
res, ret = arm.motion.get_DH_param()
if ret == StatusCodeEnum.OK:
    print("获取DH参数成功 / Get DH parameters successful")
else:
    print(f"获取DH参数失败，错误代码 / Get DH parameters failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 设置DH参数
# [EN] Set DH parameters
ret = arm.motion.set_DH_param(res)
if ret == StatusCodeEnum.OK:
    print("设置DH参数成功 / Set DH parameters successful")
else:
    print(f"设置DH参数失败，错误代码 / Set DH parameters failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
for param in res:
    print(
        f"DH参数的ID / DH parameter ID: {param.id}\n"
        f"杆件长度 / Link length: {param.a}\n"
        f"杆件扭角 / Link twist angle: {param.alpha}\n"
        f"关节距离 / Joint distance: {param.d}\n"
        f"关节转角 / Joint angle: {param.offset}"
    )

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
