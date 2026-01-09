#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: R寄存器读写示例 / Example of reading and writing the R register
"""
from Agilebot import Arm, StatusCodeEnum

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the Agilebot robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the Agilebot robot
ret = arm.connect("10.27.1.254")
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 添加R寄存器
# [EN] Add R register
ret = arm.register.write_R(5, 8.6)
if ret == StatusCodeEnum.OK:
    print("写入R寄存器成功 / Write R register successful")
else:
    print(f"写入R寄存器失败，错误代码 / Write R register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取R寄存器
# [EN] Read R register
res, ret = arm.register.read_R(5)
if ret == StatusCodeEnum.OK:
    print("读取R寄存器成功 / Read R register successful")
else:
    print(f"读取R寄存器失败，错误代码 / Read R register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 打印结果
# [EN] Print the result
print(f"R寄存器值 / R register value: {res}")

# [ZH] 删除R寄存器
# [EN] Delete R register
ret = arm.register.delete_R(5)
if ret == StatusCodeEnum.OK:
    print("删除R寄存器成功 / Delete R register successful")
else:
    print(f"删除R寄存器失败，错误代码 / Delete R register failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
