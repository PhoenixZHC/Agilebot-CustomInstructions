#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 示教运动功能-多关节点动运动使用示例 / / Teaching motion function - Multi-joint motion usage example
"""
import time

from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化Arm类
# [EN] Initialize the Arm class
arm = Arm()
# [ZH] 连接控制器
# [EN] Connect to the controller
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 仅支持手动模式下进行jogging
# [EN] Only manual mode is supported for jogging
# [ZH] 点动关节坐标系下的关节1,2,3
# [EN] Jog joint 1,2,3 under the joint coordinate system
ret = arm.jogging.multi_move([1, 2, 3])
if ret == StatusCodeEnum.OK:
    print("点动运动开始成功 / Jogging movement started successfully")
else:
    print(f"点动运动开始失败，错误代码 / Jogging movement start failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 运动3s
# [EN] Move for 3 seconds
time.sleep(3)

# [ZH] 停止
# [EN] Stop
arm.jogging.stop()

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
