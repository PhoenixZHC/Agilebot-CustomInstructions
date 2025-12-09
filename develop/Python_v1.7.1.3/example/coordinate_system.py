#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import CoordinateSystemType

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 读取TF列表
tf_list, ret = arm.coordinate_system.get_coordinate_list(CoordinateSystemType.ToolFrame)
assert ret == StatusCodeEnum.OK

# 打印结果
print(f"TF列表t：{tf_list}")

# 获取指定工具坐标系
tf, ret = arm.coordinate_system.get(CoordinateSystemType.ToolFrame, 1)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"TF序号：{tf.coordinate_info.coordinate_id}\n"
    f"TF名称：{tf.coordinate_info.name}\n"
    f"X：{tf.position.x}\n"
    f"Y：{tf.position.y}\n"
    f"Z：{tf.position.z}"
    )

# 添加一个坐标系
tf_new, ret = arm.coordinate_system.add(CoordinateSystemType.ToolFrame)
assert ret == StatusCodeEnum.OK

# 打印结果
print(
    f"TF序号：{tf_new.coordinate_info.coordinate_id}\n"
    f"TF名称：{tf_new.coordinate_info.name}\n"
    f"X：{tf_new.position.x}\n"
    f"Y：{tf_new.position.y}\n"
    f"Z：{tf_new.position.z}"
    )

# 更新一个指定的坐标系
tf_new.coordinate_info.comment = "test"
tf_new.position.x = 20
ret = arm.coordinate_system.update(CoordinateSystemType.ToolFrame, tf_new)
assert ret == StatusCodeEnum.OK

# 删除一个指定的坐标系
ret =arm.coordinate_system.delete(CoordinateSystemType.ToolFrame, 1)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()
