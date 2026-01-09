#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 直线运动使用示例 / Example of linear motion usage
"""
from Agilebot import Arm, MotionPose, PoseType, StatusCodeEnum

# [ZH] 初始化Arm类
# [EN] Initialize the Arm class
arm = Arm()
# [ZH] 连接控制器
# [EN] Connect to the controller
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 初始化位姿
# [EN] Initialize pose
motion_pose = MotionPose()
motion_pose.pt = PoseType.JOINT
motion_pose.joint.j1 = 0
motion_pose.joint.j2 = 0
motion_pose.joint.j3 = 60
motion_pose.joint.j4 = 60
motion_pose.joint.j5 = 0
motion_pose.joint.j6 = 0

# [ZH] 发送运动请求
# [EN] Send motion request
ret = arm.motion.move_line(motion_pose, vel=100, acc=0.5)
if ret == StatusCodeEnum.OK:
    print("直线运动成功 / Line motion successful")
else:
    print(f"直线运动失败，错误代码 / Line motion failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 结束后断开机器人连接
# [EN] Disconnect from the robot after completion
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
