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

# 获取当前位姿
motion_pose, ret = arm.motion.get_current_pose(PoseType.JOINT)
assert ret == StatusCodeEnum.OK

# 打印结果位姿
print(f"位姿类型：{motion_pose.pt}")
print(
    f"轴位置：\n"
    f"J1:{motion_pose.joint.j1}\n"
    f"J2:{motion_pose.joint.j2}\n"
    f"J3:{motion_pose.joint.j3}\n"
    f"J4:{motion_pose.joint.j4}\n"
    f"J5:{motion_pose.joint.j5}\n"
    f"J6:{motion_pose.joint.j6}"
)

# 获取当前位姿
motion_pose, ret = arm.motion.get_current_pose(PoseType.CART, 0, 0)
assert ret == StatusCodeEnum.OK

# 打印结果位姿
print(f"位姿类型：{motion_pose.pt}")
print(
    f"坐标位置：\n"
    f"X:{motion_pose.cartData.position.x}\n"
    f"Y:{motion_pose.cartData.position.y}\n"
    f"Z:{motion_pose.cartData.position.z}\n"
    f"A:{motion_pose.cartData.position.a}\n"
    f"B:{motion_pose.cartData.position.b}\n"
    f"C:{motion_pose.cartData.position.c}"
)

# 断开捷勃特机器人连接
arm.disconnect()
