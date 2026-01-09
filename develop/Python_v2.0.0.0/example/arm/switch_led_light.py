#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Arm类下的机器人灯环状态获取示例 / Example of obtaining the status of the LED
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

# [ZH] 控制LED灯光关闭
# [EN] Control LED light off
ret = arm.switch_led_light(mode=False)
# [ZH] 检查是否成功
# [EN] Check if successful
if ret == StatusCodeEnum.OK:
    print("LED灯光关闭成功 / Control LED light off successfully")
else:
    print(f"LED灯光关闭失败，错误代码 / Control LED light off failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

time.sleep(5)

# [ZH] 控制LED灯光开启
# [EN] Control LED light on
ret = arm.switch_led_light(mode=True)
# [ZH] 检查是否成功
# [EN] Check if successful
if ret == StatusCodeEnum.OK:
    print("LED灯光开启成功 / Control LED light on successfully")
else:
    print(f"LED灯光开启失败，错误代码 / Control LED light on failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
