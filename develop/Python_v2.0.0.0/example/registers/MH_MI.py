#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: MH寄存器及MI寄存器读写示例 / Example of reading and writing to the MH register and MI register
"""
from Agilebot import Arm, StatusCodeEnum

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

# [ZH] 读取MH寄存器
# [EN] Read MH register
res, ret = arm.register.read_MH(1)
if ret == StatusCodeEnum.OK:
    print("读取MH寄存器成功 / Read MH register successful")
else:
    print(f"读取MH寄存器失败，错误代码 / Read MH register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(f"MH寄存器 / MH register: {res}")

# [ZH] 写入MH寄存器
# [EN] Write MH register
ret = arm.register.write_MH(1, 16)
if ret == StatusCodeEnum.OK:
    print("写入MH寄存器成功 / Write MH register successful")
else:
    print(f"写入MH寄存器失败，错误代码 / Write MH register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取MI寄存器
# [EN] Read MI register
res, ret = arm.register.read_MI(1)
if ret == StatusCodeEnum.OK:
    print("读取MI寄存器成功 / Read MI register successful")
else:
    print(f"读取MI寄存器失败，错误代码 / Read MI register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print result
print(f"MI寄存器 / MI register: {res}")

# [ZH] 写入MI寄存器
# [EN] Write MI register
ret = arm.register.write_MI(1, 18)
if ret == StatusCodeEnum.OK:
    print("写入MI寄存器成功 / Write MI register successful")
else:
    print(f"写入MI寄存器失败，错误代码 / Write MI register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
