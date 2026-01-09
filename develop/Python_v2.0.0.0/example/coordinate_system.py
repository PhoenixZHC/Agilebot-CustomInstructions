#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 坐标系系统使用示例 / Example of coordinate system usage
"""
from Agilebot import Arm, Coordinate, Position, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the robot
arm = Arm()

# [ZH] 连接捷勃特机器人
# [EN] Connect to the robot
ret = arm.connect("10.27.1.254")
if ret != StatusCodeEnum.OK:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("机器人连接成功 / Robot connected successfully")

# [ZH] 定义位姿数据用于计算工具坐标系
# [EN] Define pose data for calculating tool coordinate system
pose_data = [
    Position(341.6861424047297, -33.70972073115479, 430.1721970894897, 0.001, 6.745, -180.000),
    Position(365.4597874970455, 77.95089759481547, 441.39040857936857, -7.343, 12.620, 138.857),
    Position(410.64702354574865, 10.394172666192766, 468.26089261578807, 18.719, 29.151, 155.585),
    Position(483.2519847999948, 112.71925218513972, 448.39071038067624, 33.947, 69.714, 133.597),
]

# [ZH] 根据位姿数据计算工具坐标系
# [EN] Calculate tool coordinate system based on pose data
pose, ret = arm.coordinate_system.TF.calculate(pose_data)
if ret != StatusCodeEnum.OK:
    print(f"计算工具坐标系失败，错误代码 / Calculate tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("计算工具坐标系成功 / Calculate tool coordinate system successfully")
print(f"计算得到的位姿 / Calculated pose：X={pose.x}, Y={pose.y}, Z={pose.z}, A={pose.a}, B={pose.b}, C={pose.c}")

# [ZH] 创建工具坐标系对象
# [EN] Create tool coordinate system object
tf = Coordinate(5, "test_tf", "测试工具坐标系", pose)

# [ZH] 删除可能存在的ID为5的坐标系（避免冲突）
# [EN] Delete coordinate system with ID 5 if exists (avoid conflict)
arm.coordinate_system.TF.delete(5)

# [ZH] 添加工具坐标系名字 / Add tool coordinate system
ret = arm.coordinate_system.TF.add(tf)
if ret != StatusCodeEnum.OK:
    print(f"添加工具坐标系失败，错误代码 / Add tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("添加工具坐标系成功 / Add tool coordinate system successfully")

# [ZH] 获取工具坐标系列表
# [EN] Get tool coordinate system list
tf_list, ret = arm.coordinate_system.TF.get_coordinate_list()
if ret != StatusCodeEnum.OK:
    print(f"获取工具坐标系列表失败，错误代码 / Get tool coordinate system list failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("获取工具坐标系列表成功 / Get tool coordinate system list successfully")
print(f"工具坐标系列表 / Tool coordinate system list: {tf_list}")

# [ZH] 获取指定的工具坐标系
# [EN] Get a specific tool coordinate system
tf, ret = arm.coordinate_system.TF.get(5)
if ret != StatusCodeEnum.OK:
    print(f"获取工具坐标系失败，错误代码 / Get tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("获取工具坐标系成功 / Get tool coordinate system successfully")
print(f"  TF ID: {tf.id}")
print(f"  TF Name: {tf.name}")
print(f"  TF Comment: {tf.comment}")
print(f"  X: {tf.data.x}, Y: {tf.data.y}, Z: {tf.data.z}")
print(f"  A: {tf.data.a}, B: {tf.data.b}, C: {tf.data.c}")

# [ZH] 更新工具坐标系的名称
# [EN] Update tool coordinate system name
tf.name = "updated_test_tf"
ret = arm.coordinate_system.TF.update(tf)
if ret != StatusCodeEnum.OK:
    print(f"更新工具坐标系失败，错误代码 / Update tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("更新工具坐标系成功 / Update tool coordinate system successfully")

# [ZH] 删除工具坐标系
# [EN] Delete tool coordinate system
ret = arm.coordinate_system.TF.delete(5)
if ret != StatusCodeEnum.OK:
    print(f"删除工具坐标系失败，错误代码 / Delete tool coordinate system failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

print("删除工具坐标系成功 / Delete tool coordinate system successfully")

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
