#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Arm类下的基础通讯连接断开示例 / Example of a basic communication connection
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("192.168.110.100")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 检查连接状态
# [EN] Check connection status
connect_status = arm.is_connected()
# [ZH] 打印结果
# [EN] Print the result
print(f"当前连接状态 / Current connection status: {connect_status}")

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
