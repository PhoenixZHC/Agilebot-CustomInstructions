#!python
from multiprocessing.connection import wait
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import MotionPose
from Agilebot.IR.A.sdk_types import PoseType
import time

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 初始化位姿
motion_pose = MotionPose()
motion_pose.pt = PoseType.CART
motion_pose.cartData.position.x = 377.000
motion_pose.cartData.position.y = 202.820
motion_pose.cartData.position.z = 507.155
motion_pose.cartData.position.c = 0
motion_pose.cartData.position.b = 0
motion_pose.cartData.position.a = 0

# 运动到初始点
ret = arm.motion.move_joint(motion_pose)
assert ret == StatusCodeEnum.OK

# 修改为运动中间点
motion_pose.cartData.position.x = 488.300
motion_pose.cartData.position.y = 359.120
motion_pose.cartData.position.z = 507.155

# 运动终点
motion_pose2 = MotionPose()
motion_pose2.pt = PoseType.CART
motion_pose2.cartData.position.x = 629.600
motion_pose2.cartData.position.y = 509.270
motion_pose2.cartData.position.z = 507.155
motion_pose2.cartData.position.c = 0
motion_pose2.cartData.position.b = 0
motion_pose2.cartData.position.a = 0

# 等待运动结束
time.sleep(10)

# 开始运动
ret_code = arm.motion.move_circle(motion_pose, motion_pose2, vel = 100)
assert ret_code == StatusCodeEnum.OK
print(f"运动成功")

# 断开捷勃特机器人连接
arm.disconnect()
