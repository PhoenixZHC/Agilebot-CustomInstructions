#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 负载识别使用示例 / Example of load identification usage
"""
import time

from Agilebot import Arm, MotionPose, PoseType, ServoStatusEnum, StatusCodeEnum

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

motion_pose = MotionPose()
motion_pose.pt = PoseType.JOINT

motion_pose.joint.j1 = 0
motion_pose.joint.j2 = 0
motion_pose.joint.j3 = 0
motion_pose.joint.j4 = 0
motion_pose.joint.j5 = 0
motion_pose.joint.j6 = 0

# [ZH] 运动到指定点
# [EN] Move to specified position
code = arm.motion.move_joint(motion_pose)
if ret == StatusCodeEnum.OK:
    print("运动到指定点成功 / Move to specified position successful")
else:
    print(f"运动到指定点失败，错误代码 / Move to specified position failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

while True:
    # [ZH] 获取伺服状态
    # [EN] Get servo status
    state, ret = arm.get_servo_status()
    if ret == StatusCodeEnum.OK:
        print("获取伺服状态成功 / Get servo status successful")
    else:
        print(f"获取伺服状态失败，错误代码 / Get servo status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)

    if state == ServoStatusEnum.SERVO_IDLE:
        break
    else:
        time.sleep(1)

# [ZH] 开始负载测定并获取结果
# [EN] Start payload identification and get result
res, ret = arm.motion.payload.payload_identify(-1, 90)
if ret == StatusCodeEnum.OK:
    print("负载识别成功 / Payload identification successful")
else:
    print(f"负载识别失败，错误代码 / Payload identification failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
