#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 圆弧运动使用示例 / Example of circular arc motion usage
"""
import time
from multiprocessing.connection import wait

from Agilebot import Arm, MotionPose, PoseType, StatusCodeEnum

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

# [ZH] 初始化位姿
# [EN] Initialize pose
motion_pose = MotionPose()
motion_pose.pt = PoseType.CART
motion_pose.cartData.position.x = 377.000
motion_pose.cartData.position.y = 202.820
motion_pose.cartData.position.z = 507.155
motion_pose.cartData.position.c = 0
motion_pose.cartData.position.b = 0
motion_pose.cartData.position.a = 0

# [ZH] 运动到初始点
# [EN] Move to initial position
ret = arm.motion.move_joint(motion_pose)
if ret == StatusCodeEnum.OK:
    print("运动到初始点成功 / Move to initial position successful")
else:
    print(f"运动到初始点失败，错误代码 / Move to initial position failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 修改为运动中间点
# [EN] Modify to intermediate motion point
motion_pose.cartData.position.x = 488.300
motion_pose.cartData.position.y = 359.120
motion_pose.cartData.position.z = 507.155

# [ZH] 运动终点
# [EN] End position
motion_pose2 = MotionPose()
motion_pose2.pt = PoseType.CART
motion_pose2.cartData.position.x = 629.600
motion_pose2.cartData.position.y = 509.270
motion_pose2.cartData.position.z = 507.155
motion_pose2.cartData.position.c = 0
motion_pose2.cartData.position.b = 0
motion_pose2.cartData.position.a = 0

# [ZH] 等待运动结束
# [EN] Wait for motion to complete
time.sleep(10)

# [ZH] 开始运动
# [EN] Start motion
ret_code = arm.motion.move_circle(motion_pose, motion_pose2, vel=100)
if ret_code == StatusCodeEnum.OK:
    print("圆弧运动成功 / Circle motion successful")
else:
    print(f"圆弧运动失败，错误代码 / Circle motion failed, error code: {ret_code.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
