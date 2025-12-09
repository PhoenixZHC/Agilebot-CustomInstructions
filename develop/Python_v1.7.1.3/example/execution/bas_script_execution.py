#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.bas_script import BasScript
from Agilebot.IR.A.script_types import *

# 初始化Arm类
arm = Arm()
# 连接控制器
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 创建BasScript对象
bs = BasScript(name='bas_test')
ret = bs.assign_value(AssignType.R, 1, OtherType.VALUE, 10)
ret = bs.move_joint(pose_type = MovePoseType.PR, pose_index = 1, speed_type = SpeedType.VALUE, speed_value = 100, smooth_type = SmoothType.SMOOTH_DISTANCE, smooth_distance = 200.5)
ret = bs.wait_time(ValueType.VALUE, 10)
assert ret == StatusCodeEnum.OK

# 执行脚本
ret = arm.execution.execute_bas_script(bs)

# 打印结果
print(f"执行结果：{ret.errmsg}")

# 结束后断开机器人连接
arm.disconnect()
