#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.common.const import const

# 初始化Arm类
arm = Arm()
# 连接控制器
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取所有负载
res, ret = arm.motion.payload.get_all_payload()
assert ret == StatusCodeEnum.OK

# 打印结果
for payload in res:
    print(
            f"负载ID:{payload[0]}\n"
            f"负载注释:{payload[1]}\n"
        )

# 结束后断开机器人连接
arm.disconnect()
