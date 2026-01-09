#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 机器人位姿使用示例 / Example of robot pose usage
"""
from Agilebot import Arm, PoseType, StatusCodeEnum

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

program_name = "test_prog"

# [ZH] 读取所有位姿
# [EN] Read all poses
poses, ret = arm.program_pose.read_all_poses(program_name)
if ret == StatusCodeEnum.OK:
    print("读取所有位姿成功 / Read all poses successfully")
    # [ZH] 打印位姿信息
    # [EN] Print pose information
    for p in poses:
        print(f"位姿ID / Pose ID：{p.id}\n" f"位姿名称 / Pose name：{p.name}")
else:
    print(f"读取所有位姿失败，错误代码 / Read all poses failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取单个位姿
# [EN] Read a single pose
pose, ret = arm.program_pose.read(program_name, 1)
if ret == StatusCodeEnum.OK:
    print("读取单个位姿成功 / Read single pose successfully")
    # [ZH] 打印位姿信息
    # [EN] Print pose information
    print(
        f"位姿ID / Pose ID：{pose.id}\n"
        f"位姿名称 / Pose name：{pose.name}\n"
        f"位姿类型 / Pose type：{pose.poseData.pt}\n"
        f"X：{pose.poseData.cartData.baseCart.position.x}\n"
        f"Y：{pose.poseData.cartData.baseCart.position.y}\n"
        f"Z：{pose.poseData.cartData.baseCart.position.z}\n"
        f"J1：{pose.poseData.joint.j1}\n"
        f"J2：{pose.poseData.joint.j2}\n"
        f"J3：{pose.poseData.joint.j3}\n"
    )
else:
    print(f"读取单个位姿失败，错误代码 / Read single pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 修改位姿
# [EN] Modify pose
pose.comment = "SDK_TEST_COMMENT"
ret = arm.program_pose.write(program_name, 1, pose)
if ret == StatusCodeEnum.OK:
    print("修改位姿成功 / Modify pose successfully")
else:
    print(f"修改位姿失败，错误代码 / Modify pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 转换位姿
# [EN] Convert pose
converted_pose, ret = arm.program_pose.convert_pose(pose, PoseType.CART, PoseType.JOINT)
if ret == StatusCodeEnum.OK:
    print("转换位姿成功 / Convert pose successfully")
else:
    print(f"转换位姿失败，错误代码 / Convert pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印位姿信息
# [EN] Print pose information
print(
    f"位姿ID / Pose ID：{converted_pose.id}\n"
    f"位姿名称 / Pose name：{converted_pose.name}\n"
    f"位姿类型 / Pose type：{converted_pose.poseData.pt}\n"
    f"X：{converted_pose.poseData.cartData.baseCart.position.x}\n"
    f"Y：{converted_pose.poseData.cartData.baseCart.position.y}\n"
    f"Z：{converted_pose.poseData.cartData.baseCart.position.z}\n"
    f"J1：{converted_pose.poseData.joint.j1}\n"
    f"J2：{converted_pose.poseData.joint.j2}\n"
    f"J3：{converted_pose.poseData.joint.j3}\n"
)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
