#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 单信号IO读写示例 / Example of single-signal I/O reading and writing
"""
from Agilebot import Arm, SignalType, SignalValue, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the robot
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取IO
# [EN] Read IO
do_value, ret = arm.signals.read(SignalType.DO, 1)
if ret == StatusCodeEnum.OK:
    print("读取IO成功 / Read IO successfully")
    print(f"DO 1 状态 / DO 1 status：{do_value}")
else:
    print(f"读取IO失败，错误代码 / Read IO failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 写入IO
# [EN] Write IO
ret = arm.signals.write(SignalType.DO, 1, SignalValue.ON)
if ret == StatusCodeEnum.OK:
    print("写入IO成功 / Write IO successfully")
else:
    print(f"写入IO失败，错误代码 / Write IO failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
