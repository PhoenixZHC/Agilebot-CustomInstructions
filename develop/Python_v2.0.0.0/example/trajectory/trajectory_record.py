#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 轨迹记录相关使用示例 / Example of real-time trajectory records usage
"""
import time

from Agilebot import Arm, RobotStatusEnum, ServoStatusEnum, StatusCodeEnum
from Agilebot.IR.A.hardware_state import HardwareState, HWState

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 订阅轨迹记录状态
# [EN] Subscribe to the trajectory record status
hw_state = HardwareState("10.27.1.254")
hw_state.subscribe(topic_list=[HWState.TOPIC_TRAJECTORY_RECORDS_STATUS])

# [ZH] 开始记录轨迹
# [EN] Start recording trajectory
ret = arm.trajectory.trajectory_record_begin("test")
if ret == StatusCodeEnum.OK:
    print("开始轨迹记录成功 / Start trajectory record successful")
else:
    print(f"开始轨迹记录失败，错误代码 / Start trajectory record failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
time.sleep(10)

res = hw_state.recv()
print(f"轨迹记录状态 / Trajectory record status: {res}")

# [ZH] 结束记录轨迹
# [EN] End recording trajectory
ret = arm.trajectory.trajectory_record_finish("test")
if ret == StatusCodeEnum.OK:
    print("结束轨迹记录成功 / End trajectory record successful")
else:
    print(f"结束轨迹记录失败，错误代码 / End trajectory record failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

res = hw_state.recv()
print(f"轨迹记录状态 / Trajectory record status: {res}")

# [ZH] 获取轨迹列表
# [EN] Get trajectory list
record_list, ret = arm.trajectory.get_trajectory_record_list()
if ret == StatusCodeEnum.OK:
    print("获取轨迹记录列表成功 / Get trajectory record list successful")
else:
    print(f"获取轨迹记录列表失败，错误代码 / Get trajectory record list failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
assert "test" in record_list

# [ZH] 获取轨迹起始位姿
# [EN] Get trajectory start pose
pose, ret = arm.trajectory.get_trajectory_record_start_pose("test")
if ret == StatusCodeEnum.OK:
    print("获取轨迹起始位姿成功 / Get trajectory start pose successful")
else:
    print(f"获取轨迹起始位姿失败，错误代码 / Get trajectory start pose failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 移动到起始位姿
# [EN] Move to the start pose
ret = arm.motion.move_joint(pose)
if ret == StatusCodeEnum.OK:
    print("关节运动成功 / Joint motion successful")
else:
    print(f"关节运动失败，错误代码 / Joint motion failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 等待控制器到位
# [EN] Wait for the controller to be ready
while True:
    robot_status, ret = arm.get_robot_status()
    if ret == StatusCodeEnum.OK:
        print("获取机器人状态成功 / Get robot status successful")
    else:
        print(f"获取机器人状态失败，错误代码 / Get robot status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)
    print(f"robot_status arm: {robot_status}")
    servo_status, ret = arm.get_servo_status()
    if ret == StatusCodeEnum.OK:
        print("获取伺服状态成功 / Get servo status successful")
    else:
        print(f"获取伺服状态失败，错误代码 / Get servo status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)
    print(f"伺服状态 / Servo status: {servo_status}")
    if robot_status == RobotStatusEnum.ROBOT_IDLE and servo_status == ServoStatusEnum.SERVO_IDLE:
        break
    time.sleep(2)

# [ZH] 开始回放轨迹
# [EN] Start replay trajectory
ret = arm.trajectory.trajectory_replay_start("test")
if ret == StatusCodeEnum.OK:
    print("开始轨迹回放成功 / Start trajectory replay successful")
else:
    print(f"开始轨迹回放失败，错误代码 / Start trajectory replay failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

time.sleep(5)

# [ZH] 停止回放轨迹
# [EN] Stop replay trajectory
ret = arm.trajectory.trajectory_replay_stop("test")
if ret == StatusCodeEnum.OK:
    print("停止轨迹回放成功 / Stop trajectory replay successful")
else:
    print(f"停止轨迹回放失败，错误代码 / Stop trajectory replay failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 删除轨迹
# [EN] Delete trajectory
ret = arm.trajectory.trajectory_record_delete("test")
if ret == StatusCodeEnum.OK:
    print("删除轨迹记录成功 / Delete trajectory record successful")
else:
    print(f"删除轨迹记录失败，错误代码 / Delete trajectory record failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
