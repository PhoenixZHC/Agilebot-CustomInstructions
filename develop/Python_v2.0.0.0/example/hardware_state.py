#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 硬件状态查询示例 / Example of hardware status query
"""
from Agilebot.IR.A.hardware_state import *

# [ZH] 初始化订阅
# [EN] Initialize subscription
hw_state = HardwareState("10.27.1.254")

# [ZH] 订阅机器人状态
# [EN] Subscribe to robot status
ret = hw_state.subscribe()
if ret == StatusCodeEnum.OK:
    print("订阅机器人状态成功 / Subscribe to robot status successfully")
else:
    print(f"订阅机器人状态失败，错误代码 / Subscribe to robot status failed, error code: {ret.errmsg}")
    hw_state.unsubscribe()
    exit(1)

# [ZH] 打印订阅的消息
# [EN] Print subscribed messages
for i in range(10):
    res = hw_state.recv()
    print(res)

# [ZH] 关闭订阅
# [EN] Close subscription
hw_state.unsubscribe()

# [ZH] 订阅IO状态
# [EN] Subscribe to IO status
io_topic = []
io_topic.extend([(IOTopic.DI, i) for i in range(1, 2)])
ret = hw_state.subscribe(io_topic=io_topic)
if ret == StatusCodeEnum.OK:
    print("订阅IO状态成功 / Subscribe to IO status successfully")
else:
    print(f"订阅IO状态失败，错误代码 / Subscribe to IO status failed, error code: {ret.errmsg}")
    hw_state.unsubscribe()
    exit(1)

# [ZH] 打印订阅的消息
# [EN] Print subscribed messages
for i in range(10):
    print(hw_state.recv())

# [ZH] 关闭订阅
# [EN] Close subscription
hw_state.unsubscribe()
