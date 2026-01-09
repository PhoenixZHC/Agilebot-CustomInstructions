#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 离线轨迹使用示例 / Example of offline trajectory usage
"""
import time

from Agilebot import Arm, RobotStatusEnum, ServoStatusEnum, StatusCodeEnum

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

# [ZH] 设置离线轨迹文件
# [EN] Set the offline trajectory file
ret = arm.trajectory.set_offline_trajectory_file("test_torque.trajectory")
if ret == StatusCodeEnum.OK:
    print("设置离线轨迹文件成功 / Set offline trajectory file successful")
else:
    print(f"设置离线轨迹文件失败，错误代码 / Set offline trajectory file failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 准备进行离线轨迹运行
# [EN] Prepare for offline trajectory execution
ret = arm.trajectory.prepare_offline_trajectory()
if ret == StatusCodeEnum.OK:
    print("准备离线轨迹运行成功 / Prepare offline trajectory execution successful")
else:
    print(f"准备离线轨迹运行失败，错误代码 / Prepare offline trajectory execution failed, error code: {ret.errmsg}")
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

# [ZH] 执行离线轨迹
# [EN] Execute the offline trajectory
ret = arm.trajectory.execute_offline_trajectory()
if ret == StatusCodeEnum.OK:
    print("执行离线轨迹成功 / Execute offline trajectory successful")
else:
    print(f"执行离线轨迹失败，错误代码 / Execute offline trajectory failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
