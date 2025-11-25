#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import PoseRegister, Posture, PoseType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 添加PR寄存器
# 创建位姿
pose_register = PoseRegister()
posture = Posture()
posture.arm_back_front = 1
pose_register.poseRegisterData.posture = posture
pose_register.id = 5
pose_register.poseRegisterData.pt = PoseType.CART
pose_register.poseRegisterData.cartData.position.x = 100
pose_register.poseRegisterData.cartData.position.y = 200
pose_register.poseRegisterData.cartData.position.z = 300
ret = arm.register.write_PR(pose_register)
assert ret == StatusCodeEnum.OK

# 读取PR寄存器
res, ret = arm.register.read_PR(5)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"位姿寄存器ID：{res.id}\n"
    f"位姿类型：{res.poseRegisterData.pt}\n"
    f"X：{res.poseRegisterData.cartData.position.x}\n"
    f"Y：{res.poseRegisterData.cartData.position.y}\n"
    f"Z：{res.poseRegisterData.cartData.position.z}\n"
    )

# 删除PR寄存器
ret = arm.register.delete_PR(5)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
