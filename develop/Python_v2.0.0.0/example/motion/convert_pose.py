#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 转换关节值坐标使用示例 / Example of converting joint coordinates
"""
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
motion_pose.cartData.position.x = 221.5
motion_pose.cartData.position.y = -494.1
motion_pose.cartData.position.z = 752.0
motion_pose.cartData.position.a = -89.1
motion_pose.cartData.position.b = 31.6
motion_pose.cartData.position.c = -149.3

# [ZH] 转换关节值坐标
# [EN] Convert to joint coordinates
joint_pose, ret = arm.motion.convert_cart_to_joint(motion_pose)
if ret == StatusCodeEnum.OK:
    print("转换关节值坐标成功 / Convert to joint coordinates successful")
else:
    print(f"转换关节值坐标失败，错误代码 / Convert to joint coordinates failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果位姿
# [EN] Print result pose
print(f"位姿类型 / Pose type: {joint_pose.pt}")
print(
    f"轴位置 / Axis position: \n"
    f"J1:{joint_pose.joint.j1}\n"
    f"J2:{joint_pose.joint.j2}\n"
    f"J3:{joint_pose.joint.j3}\n"
    f"J4:{joint_pose.joint.j4}\n"
    f"J5:{joint_pose.joint.j5}\n"
    f"J6:{joint_pose.joint.j6}"
)

# [ZH] 转换笛卡尔坐标
# [EN] Convert to Cartesian coordinates
cart_pose, ret = arm.motion.convert_joint_to_cart(joint_pose)
if ret == StatusCodeEnum.OK:
    print("转换笛卡尔坐标成功 / Convert to Cartesian coordinates successful")
else:
    print(f"转换笛卡尔坐标失败，错误代码 / Convert to Cartesian coordinates failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果位姿
# [EN] Print result pose
print(f"位姿类型 / Pose type: {cart_pose.pt}")
print(
    f"笛卡尔位置 / Cartesian position: \n"
    f"X:{cart_pose.cartData.position.x}\n"
    f"Y:{cart_pose.cartData.position.y}\n"
    f"Z:{cart_pose.cartData.position.z}\n"
    f"A:{cart_pose.cartData.position.a}\n"
    f"B:{cart_pose.cartData.position.b}\n"
    f"C:{cart_pose.cartData.position.c}"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
