#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Arm类下的控制伺服操作示例 / Eexample of control servo operation example
"""
import time

from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 机器人伺服重置
# [EN] Robot servo reset
ret = arm.servo_reset()
if ret == StatusCodeEnum.OK:
    print("伺服重置成功 / Servo reset successfully")
else:
    print(f"伺服重置失败，错误代码 / Servo reset failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
time.sleep(5)

# [ZH] 机器人伺服下电
# [EN] Robot servo power off
ret = arm.servo_off()
if ret == StatusCodeEnum.OK:
    print("伺服下电成功 / Servo power off successfully")
else:
    print(f"伺服下电失败，错误代码 / Servo power off failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
time.sleep(5)

# [ZH] 机器人伺服上电
# [EN] Robot servo power on
ret = arm.servo_on()
if ret == StatusCodeEnum.OK:
    print("伺服上电成功 / Servo power on successfully")
else:
    print(f"伺服上电失败，错误代码 / Servo power on failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
