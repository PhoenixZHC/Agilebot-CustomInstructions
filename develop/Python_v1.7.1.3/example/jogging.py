#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.jogging import MoveMode
from Agilebot.IR.A.sdk_types import TCSType
from Agilebot.IR.A.status_code import StatusCodeEnum
import time

# 初始化Arm类
arm = Arm()
# 连接控制器
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置关节坐标系
assert arm.motion.set_TCS(TCSType.JOINT) == StatusCodeEnum.OK

# 仅支持手动模式下进行jogging
# 点动关节坐标系下的关节1
assert arm.jogging.move(1, MoveMode.Continuous) == StatusCodeEnum.OK

# 运动3s
time.sleep(3)

# 停止
arm.jogging.stop()

arm.disconnect()