#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import PoseType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

program_name = 'test_prog'

# 读取所有位姿
poses, ret = arm.program_pose.read_all_poses(program_name)
assert ret == StatusCodeEnum.OK

# 打印位姿信息
for p in poses:
    print(
        f"位姿ID：{p.id}\n"
        f"位姿名称：{p.name}"
    )

# 读取单个位姿
pose, ret = arm.program_pose.read(program_name, 1)
assert ret == StatusCodeEnum.OK

# 打印位姿信息
print(
        f"位姿ID：{pose.id}\n"
        f"位姿名称：{pose.name}\n"
        f"位姿类型：{pose.poseData.pt}\n"
        f"X：{pose.poseData.cartData.baseCart.position.x}\n"
        f"Y：{pose.poseData.cartData.baseCart.position.y}\n"
        f"Z：{pose.poseData.cartData.baseCart.position.z}\n"
        f"J1：{pose.poseData.joint.j1}\n"
        f"J2：{pose.poseData.joint.j2}\n"
        f"J3：{pose.poseData.joint.j3}\n"
    )

# 修改位姿
pose.comment = "SDK_TEST_COMMENT"
ret = arm.program_pose.write(program_name, 1, pose)
assert ret == StatusCodeEnum.OK

# 转换位姿
converted_pose, ret = arm.program_pose.convert_pose(pose, PoseType.CART, PoseType.JOINT)
assert ret == StatusCodeEnum.OK

# 打印位姿信息
print(
        f"位姿ID：{converted_pose.id}\n"
        f"位姿名称：{converted_pose.name}\n"
        f"位姿类型：{converted_pose.poseData.pt}\n"
        f"X：{converted_pose.poseData.cartData.baseCart.position.x}\n"
        f"Y：{converted_pose.poseData.cartData.baseCart.position.y}\n"
        f"Z：{converted_pose.poseData.cartData.baseCart.position.z}\n"
        f"J1：{converted_pose.poseData.joint.j1}\n"
        f"J2：{converted_pose.poseData.joint.j2}\n"
        f"J3：{converted_pose.poseData.joint.j3}\n"
    )

# 断开捷勃特机器人连接
arm.disconnect()
