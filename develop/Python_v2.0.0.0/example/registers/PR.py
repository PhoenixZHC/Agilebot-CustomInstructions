#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: PR寄存器读写示例 / Example of reading and writing to the PR register
"""
from Agilebot import Arm, PoseRegister, PoseType, Posture, StatusCodeEnum

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

# [ZH] 添加PR寄存器
# [EN] Add PR register
# [ZH] 创建位姿
# [EN] Create pose
pose_register = PoseRegister()
posture = Posture()
posture.arm_back_front = 1
pose_register.poseRegisterData.cartData.posture = posture
pose_register.id = 5
pose_register.poseRegisterData.pt = PoseType.CART
pose_register.poseRegisterData.cartData.position.x = 100
pose_register.poseRegisterData.cartData.position.y = 200
pose_register.poseRegisterData.cartData.position.z = 300
ret = arm.register.write_PR(pose_register)
if ret == StatusCodeEnum.OK:
    print("写入PR寄存器成功 / Write PR register successful")
else:
    print(f"写入PR寄存器失败，错误代码 / Write PR register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取PR寄存器
# [EN] Read PR register
res, ret = arm.register.read_PR(5)
if ret == StatusCodeEnum.OK:
    print("读取PR寄存器成功 / Read PR register successful")
else:
    print(f"读取PR寄存器失败，错误代码 / Read PR register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(
    f"位姿寄存器ID / Pose register ID: {res.id}\n"
    f"位姿类型 / Pose type: {res.poseRegisterData.pt}\n"
    f"X / X: {res.poseRegisterData.cartData.position.x}\n"
    f"Y / Y: {res.poseRegisterData.cartData.position.y}\n"
    f"Z / Z: {res.poseRegisterData.cartData.position.z}\n"
    f"C / C: {res.poseRegisterData.cartData.position.c}\n"
    f"B / B: {res.poseRegisterData.cartData.position.b}\n"
    f"A / A: {res.poseRegisterData.cartData.position.a}\n"
)

# [ZH] 删除PR寄存器
# [EN] Delete PR register
ret = arm.register.delete_PR(5)
if ret == StatusCodeEnum.OK:
    print("删除PR寄存器成功 / Delete PR register successful")
else:
    print(f"删除PR寄存器失败，错误代码 / Delete PR register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
