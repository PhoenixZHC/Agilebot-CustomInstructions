#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import MotionPose
from Agilebot.IR.A.sdk_types import PoseType
from Agilebot.IR.A.sdk_types import ServoStatusEnum
import time

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

motion_pose = MotionPose()
motion_pose.pt = PoseType.JOINT

motion_pose.joint.j1 = 0
motion_pose.joint.j2 = 0
motion_pose.joint.j3 = 0
motion_pose.joint.j4 = 0
motion_pose.joint.j5 = 0
motion_pose.joint.j6 = 0

# 运动到指定点
code = arm.motion.move_joint(motion_pose)
assert ret == StatusCodeEnum.OK

while True:
    # 获取伺服状态
    state, ret = arm.get_servo_status()
    assert ret == StatusCodeEnum.OK

    if state == ServoStatusEnum.SERVO_IDLE:
        break
    else:
        time.sleep(1)

# 开始负载测定并获取结果
res, ret =  arm.motion.payload.payload_identify(-1, 90)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
