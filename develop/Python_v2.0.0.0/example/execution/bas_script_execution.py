#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: Bas脚本创建和使用示例 / Example of Bas script creation and usage
"""
from Agilebot import *

# [ZH] 初始化Arm类
# [EN] Initialize the Arm class
arm = Arm()
# [ZH] 连接控制器
# [EN] Connect to the controller
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 创建BasScript对象
# [EN] Create BasScript object
bs = BasScript(name="bas_test")
ret = bs.assign_value(AssignType.R, 1, OtherType.VALUE, 10)
ret = bs.move_joint(
    pose_type=MovePoseType.PR,
    pose_index=1,
    speed_type=SpeedType.VALUE,
    speed_value=100,
    smooth_type=SmoothType.SMOOTH_DISTANCE,
    smooth_distance=200.5,
)
ret = bs.wait_time(ValueType.VALUE, 10)
if ret == StatusCodeEnum.OK:
    print("创建BasScript对象成功 / Create BasScript object successfully")
else:
    print(f"创建BasScript对象失败，错误代码 / Create BasScript object failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 执行脚本
# [EN] Execute script
ret = arm.execution.execute_bas_script(bs)
if ret == StatusCodeEnum.OK:
    print("执行脚本成功 / Execute script successfully")
else:
    print(f"执行脚本失败，错误代码 / Execute script failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)


# [ZH] 结束后断开机器人连接
# [EN] Disconnect from the robot after completion
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
