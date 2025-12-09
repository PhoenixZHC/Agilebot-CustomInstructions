#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 获取DH参数
res, ret = arm.motion.get_DH_param()
assert ret == StatusCodeEnum.OK

# 设置DH参数
ret = arm.motion.set_DH_param(res)
assert ret == StatusCodeEnum.OK

# 打印结果
for param in res:
    print(
        f"DH参数的ID:{param.id}\n"
        f"杆件长度:{param.a}\n"
        f"杆件扭角:{param.alpha}\n"
        f"关节距离:{param.d}\n"
        f"关节转角:{param.offset}"
    )

# 断开捷勃特机器人连接
arm.disconnect()