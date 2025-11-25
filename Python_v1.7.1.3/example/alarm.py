#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取所有的活动的报警
alarms, ret = arm.alarm.get_all_active_alarms()
assert ret == StatusCodeEnum.OK
for alarm in alarms:
    print(alarm)

# 重置报警
ret = arm.alarm.reset()
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
