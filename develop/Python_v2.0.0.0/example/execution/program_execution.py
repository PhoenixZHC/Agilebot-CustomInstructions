#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 自定义程序使用示例 / Example of custom program usage
"""
import time

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
    print("机器人连接成功 / Robot connection successful")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

program_name = "test"

# [ZH] 执行程序
# [EN] Execute program
ret = arm.execution.start(program_name)
if ret == StatusCodeEnum.OK:
    print("程序启动成功 / Program start successful")
else:
    print(f"程序启动失败，错误代码 / Program start failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 获取所有正在运行的程序
# [EN] Get all running programs
programs_list, ret = arm.execution.all_running_programs()
if ret == StatusCodeEnum.OK:
    print("获取运行程序列表成功 / Get running programs list successful")
else:
    print(f"获取运行程序列表失败，错误代码 / Get running programs list failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
for program in programs_list:
    print(f"正在运行的程序名：{program}")

time.sleep(2)

# [ZH] 暂停程序
# [EN] Pause program
ret = arm.execution.pause(program_name)
if ret == StatusCodeEnum.OK:
    print("程序暂停成功 / Program pause successful")
else:
    print(f"程序暂停失败，错误代码 / Program pause failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

time.sleep(2)

# [ZH] 恢复程序
# [EN] Resume program
ret = arm.execution.resume(program_name)
if ret == StatusCodeEnum.OK:
    print("程序恢复成功 / Program resume successful")
else:
    print(f"程序恢复失败，错误代码 / Program resume failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

time.sleep(2)

# [ZH] 停止程序
# [EN] Stop program
ret = arm.execution.stop(program_name)
if ret == StatusCodeEnum.OK:
    print("程序停止成功 / Program stop successful")
else:
    print(f"程序停止失败，错误代码 / Program stop failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 断开捷勃特机器人连接
# [EN] Disconnect from the Agilebot robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
