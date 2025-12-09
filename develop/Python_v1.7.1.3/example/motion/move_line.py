#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import MotionPose
from Agilebot.IR.A.sdk_types import PoseType

# 初始化Arm类
arm = Arm()
# 连接控制器
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 初始化位姿
motion_pose = MotionPose()
motion_pose.pt = PoseType.JOINT
motion_pose.joint.j1 = 0
motion_pose.joint.j2 = 0
motion_pose.joint.j3 = 60
motion_pose.joint.j4 = 60
motion_pose.joint.j5 = 0
motion_pose.joint.j6 = 0

# 发送运动请求
ret = arm.motion.move_line(motion_pose, vel = 100, acc = 0.5)
assert ret == StatusCodeEnum.OK

print(f"运动成功")

# 结束后断开机器人连接
arm.disconnect()
