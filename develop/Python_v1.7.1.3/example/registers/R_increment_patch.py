#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum


def increment_R(self, id: int, step: float = 1.0):
    """
    自增R寄存器值

    参数:
    - id (int): R寄存器ID
    - step (float): 自增步长，默认为1.0

    返回:
    - StatusCodeEnum: 操作状态码
    """
    # 读取当前值
    current_value, ret = self.read_R(id)
    if ret != StatusCodeEnum.OK:
        return ret

    # 计算新值
    new_value = float(current_value) + float(step)

    # 写入新值
    ret = self.write_R(id, new_value)
    return ret


# 扩展register类，添加increment_R方法
# 通过monkey patch方式给register类添加方法
arm_temp = Arm()
register_type = type(arm_temp.register)
register_type.increment_R = increment_R
del arm_temp

# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 添加R寄存器
ret = arm.register.write_R(5, 8.6)
assert ret == StatusCodeEnum.OK

# 读取R寄存器
res, ret = arm.register.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"初始R寄存器值：{res}")

# 执行自增操作（默认自增1）
ret = arm.register.increment_R(5)
assert ret == StatusCodeEnum.OK

# 读取自增后的值
res, ret = arm.register.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"自增1后R寄存器值：{res}")

# 执行自增操作（自增2.5）
ret = arm.register.increment_R(5, step=2.5)
assert ret == StatusCodeEnum.OK

# 读取自增后的值
res, ret = arm.register.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"自增2.5后R寄存器值：{res}")

# 删除R寄存器
ret = arm.register.delete_R(5)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()

