#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 路径记录相关使用示例 / Example of usage related to path records
"""
import time

from Agilebot import Arm, MoveMode, RobotStatusEnum, ServoStatusEnum, StatusCodeEnum

# [ZH] 初始化机械臂并连接到指定IP地址
# [EN] Initialize the robotic arm and connect to the specified IP address
arm = Arm()
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 开始记录轨迹，指定文件名、轨迹名、记录模式和覆盖选项
# [EN] Start trajectory recording, specifying filename, trajectory name, recording mode and overwrite option
ret = arm.trajectory.path_record_begin("test_path.path", "Path Test", 10, 1)
if ret == StatusCodeEnum.OK:
    print("开始路径记录成功 / Start path record successful")
else:
    print(f"开始路径记录失败，错误代码 / Start path record failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 检查记录状态，传入轨迹文件名列表
# [EN] Check recording status, passing in trajectory filename list
state, ret = arm.trajectory.get_path_state(["test_path.path"])
if ret == StatusCodeEnum.OK:
    print("获取路径状态成功 / Get path state successful")
else:
    print(f"获取路径状态失败，错误代码 / Get path state failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
if state["test_path.path"] == 0:
    print(f"路径表记录中 / Path table recording in progress")

# [ZH] 示教运动
# [EN] Teaching motion
ret = arm.jogging.move(3, MoveMode.Continuous)
if ret == StatusCodeEnum.OK:
    print("点动运动成功 / Jogging movement successful")
else:
    print(f"点动运动失败，错误代码 / Jogging movement failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
# 等待3秒，让机械臂持续运动
time.sleep(2)
# 停止机械臂运动
arm.jogging.stop()
time.sleep(2)
ret = arm.jogging.move(-3, MoveMode.Continuous)
if ret == StatusCodeEnum.OK:
    print("点动运动成功 / Jogging movement successful")
else:
    print(f"点动运动失败，错误代码 / Jogging movement failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
# 等待3秒，让机械臂持续运动
time.sleep(2)
# 停止机械臂运动
arm.jogging.stop()
time.sleep(2)

# [ZH] 结束轨迹记录
# [EN] Finish trajectory recording
ret = arm.trajectory.path_record_finish()
if ret == StatusCodeEnum.OK:
    print("结束路径记录成功 / Finish path record successful")
else:
    print(f"结束路径记录失败，错误代码 / Finish path record failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 检查记录状态，传入轨迹文件名列表
# [EN] Check recording status, passing in trajectory filename list
state, ret = arm.trajectory.get_path_state(["test_path.path"])
if ret == StatusCodeEnum.OK:
    print("获取路径状态成功 / Get path state successful")
else:
    print(f"获取路径状态失败，错误代码 / Get path state failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
if state["test_path.path"] == 1:
    print(f"路径表记录完成 / Path table recording completed")

# [ZH] 获取记录轨迹的起始位置姿态
# [EN] Get the starting position pose of the recorded trajectory
pose, ret = arm.trajectory.get_path_start_pose("test_path.path")
if ret == StatusCodeEnum.OK:
    print("获取路径起始位姿成功 / Get path start pose successful")
else:
    print(f"获取路径起始位姿失败，错误代码 / Get path start pose failed, error code: {ret.errmsg}")
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
    # [ZH] 检查机器人状态获取是否成功
    # [EN] Check if robot status acquisition is successful
    if ret == StatusCodeEnum.OK:
        print("获取机器人状态成功 / Get robot status successful")
    else:
        print(f"获取机器人状态失败，错误代码 / Get robot status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)
    print(f"robot_status arm: {robot_status}")
    servo_status, ret = arm.get_servo_status()
    # [ZH] 检查伺服状态获取是否成功
    # [EN] Check if servo status acquisition is successful
    if ret == StatusCodeEnum.OK:
        print("获取伺服状态成功 / Get servo status successful")
    else:
        print(f"获取伺服状态失败，错误代码 / Get servo status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)
    print(f"servo status arm: {servo_status}")
    if robot_status == RobotStatusEnum.ROBOT_IDLE and servo_status == ServoStatusEnum.SERVO_IDLE:
        break
    time.sleep(2)

# [ZH] 设置轨迹规划参数（速度比例和加速度比例）
# [EN] Set trajectory planning parameters (velocity ratio and acceleration ratio)
ret = arm.trajectory.set_path_planner_parameter(0.5, 0.3333333)
if ret == StatusCodeEnum.OK:
    print("设置路径规划参数成功 / Set path planner parameter successful")
else:
    print(f"设置路径规划参数失败，错误代码 / Set path planner parameter failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取轨迹规划参数以验证设置是否成功
# [EN] Get trajectory planning parameters to verify if the setting is successful
param1, param2, ret = arm.trajectory.get_path_planner_parameter()
if ret == StatusCodeEnum.OK:
    print("获取路径规划参数成功 / Get path planner parameter successful")
else:
    print(f"获取路径规划参数失败，错误代码 / Get path planner parameter failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 移动到记录的轨迹，指定轨迹文件名、速度和模式
# [EN] Move to the recorded trajectory, specifying trajectory filename, speed and mode
ret = arm.trajectory.move_path("test_path.path", 2000, 1)
if ret == StatusCodeEnum.OK:
    print("路径运动成功 / Path motion successful")
else:
    print(f"路径运动失败，错误代码 / Path motion failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
time.sleep(3)

# [ZH] 断开与机械臂的连接
# [EN] Disconnect from the robotic arm
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
