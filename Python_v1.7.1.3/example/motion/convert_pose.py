#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import MotionPose
from Agilebot.IR.A.sdk_types import PoseType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 初始化位姿
motion_pose = MotionPose()
motion_pose.pt = PoseType.CART
motion_pose.cartData.position.x = 221.5
motion_pose.cartData.position.y = -494.1
motion_pose.cartData.position.z = 752.0
motion_pose.cartData.position.a = -89.1
motion_pose.cartData.position.b = 31.6
motion_pose.cartData.position.c = -149.3

# 转换关节值坐标
joint_pose, ret = arm.motion.convert_cart_to_joint(motion_pose)
assert ret == StatusCodeEnum.OK

# 打印结果位姿
print(f"位姿类型：{joint_pose.pt}")
print(
    f"轴位置：\n"
    f"J1:{joint_pose.joint.j1}\n"
    f"J2:{joint_pose.joint.j2}\n"
    f"J3:{joint_pose.joint.j3}\n"
    f"J4:{joint_pose.joint.j4}\n"
    f"J5:{joint_pose.joint.j5}\n"
    f"J6:{joint_pose.joint.j6}"
)

# 转换笛卡尔坐标
cart_pose, ret = arm.motion.convert_joint_to_cart(joint_pose)
assert ret == StatusCodeEnum.OK

# 打印结果位姿
print(f"位姿类型：{cart_pose.pt}")
print(
    f"笛卡尔位置：\n"
    f"X:{cart_pose.cartData.position.x}\n"
    f"Y:{cart_pose.cartData.position.y}\n"
    f"Z:{cart_pose.cartData.position.z}\n"
    f"A:{cart_pose.cartData.position.a}\n"
    f"B:{cart_pose.cartData.position.b}\n"
    f"C:{cart_pose.cartData.position.c}"
)

# 断开捷勃特机器人连接
arm.disconnect()