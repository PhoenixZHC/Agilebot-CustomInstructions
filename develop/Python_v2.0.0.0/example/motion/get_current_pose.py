#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 当前关节位姿获取示例 / Example of current joint pose acquisition
"""
from Agilebot import Arm, PoseType, StatusCodeEnum

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

# [ZH] 获取当前位姿
# [EN] Get current pose
motion_pose, ret = arm.motion.get_current_pose(PoseType.JOINT)
if ret == StatusCodeEnum.OK:
    print("获取关节位姿成功 / Get joint pose successful")
else:
    print(f"获取关节位姿失败，错误代码 / Get joint pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果位姿
# [EN] Print result pose
print(f"位姿类型 / Pose type: {motion_pose.pt}")
print(
    f"轴位置 / Axis position:\n"
    f"J1:{motion_pose.joint.j1}\n"
    f"J2:{motion_pose.joint.j2}\n"
    f"J3:{motion_pose.joint.j3}\n"
    f"J4:{motion_pose.joint.j4}\n"
    f"J5:{motion_pose.joint.j5}\n"
    f"J6:{motion_pose.joint.j6}"
)

# [ZH] 获取当前位姿
# [EN] Get current pose
motion_pose, ret = arm.motion.get_current_pose(PoseType.CART, 0, 0)
if ret == StatusCodeEnum.OK:
    print("获取笛卡尔位姿成功 / Get Cartesian pose successful")
else:
    print(f"获取笛卡尔位姿失败，错误代码 / Get Cartesian pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果位姿
# [EN] Print result pose
print(f"位姿类型 / Pose type: {motion_pose.pt}")
print(
    f"坐标位置 / Coordinate position:\n"
    f"X:{motion_pose.cartData.position.x}\n"
    f"Y:{motion_pose.cartData.position.y}\n"
    f"Z:{motion_pose.cartData.position.z}\n"
    f"A:{motion_pose.cartData.position.a}\n"
    f"B:{motion_pose.cartData.position.b}\n"
    f"C:{motion_pose.cartData.position.c}"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
