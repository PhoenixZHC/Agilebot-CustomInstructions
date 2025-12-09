#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import ServoStatusEnum, RobotStatusEnum
import time
import os

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置离线轨迹文件
ret =arm.trajectory.set_offline_trajectory_file("test_torque.trajectory")
assert ret == StatusCodeEnum.OK

# 准备进行离线轨迹运行
ret =arm.trajectory.prepare_offline_trajectory()
assert ret == StatusCodeEnum.OK

# 等待控制器到位
while True:
    robot_status, ret = arm.get_robot_status()
    assert ret == StatusCodeEnum.OK
    print(f"robot_status arm: {robot_status}")
    servo_status, ret = arm.get_servo_status()
    assert ret == StatusCodeEnum.OK
    print(f"servo status arm: {servo_status}")
    if robot_status == RobotStatusEnum.ROBOT_IDLE and servo_status == ServoStatusEnum.SERVO_IDLE:
        break
    time.sleep(2)

# 执行离线轨迹
ret =arm.trajectory.execute_offline_trajectory()
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
