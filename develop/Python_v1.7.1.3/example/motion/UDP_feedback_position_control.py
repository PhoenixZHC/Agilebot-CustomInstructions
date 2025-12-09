#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置udp反馈参数
ret = arm.motion.set_udp_feedback_params(True, '10.27.1.254', 20, 1, [0,1,2])
assert ret == StatusCodeEnum.OK

# 进入实时位置控制模式
ret = arm.motion.enter_position_control()
assert ret == StatusCodeEnum.OK

# 在此插入发送UDP数据控制机器人代码

# 退出实时位置控制模式
ret = arm.motion.exit_position_control()
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
