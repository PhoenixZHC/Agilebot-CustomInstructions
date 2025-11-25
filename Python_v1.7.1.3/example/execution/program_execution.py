#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

program_name = 'test'

# 执行程序 
ret = arm.execution.start(program_name)
assert ret == StatusCodeEnum.OK

# 获取所有正在运行的程序
programs_list, ret = arm.execution.all_running_programs()
assert ret == StatusCodeEnum.OK
for program in programs_list:
    print(f"正在运行的程序名：{program.program_name}")

# 暂停程序 
ret = arm.execution.pause(program_name)
assert ret == StatusCodeEnum.OK

# 恢复程序
ret = arm.execution.resume(program_name)
assert ret == StatusCodeEnum.OK

# 停止程序
ret = arm.execution.stop(program_name)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
