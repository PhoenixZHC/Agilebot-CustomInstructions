#!python
from Agilebot.IR.A.hardware_state import *

# 初始化订阅
hw_state = HardwareState("10.27.1.254")

# 订阅机器人状态
ret = hw_state.subscribe()
assert ret == StatusCodeEnum.OK

# 打印订阅的消息
for i in range(10):
    print(hw_state.recv())

# 关闭订阅
hw_state.unsubscribe()

# 订阅IO状态
io_topic = []
io_topic.extend([(IOTopic.DO, i) for i in range(1, 2)])
ret = hw_state.subscribe(io_topic=io_topic)
assert ret == StatusCodeEnum.OK

# 打印订阅的消息
for i in range(10):
    print(hw_state.recv())

# 关闭订阅
hw_state.unsubscribe()
