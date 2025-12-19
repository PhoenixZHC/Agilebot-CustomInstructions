#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum


class RegisterExtension:
    """Register扩展类，添加increment_R方法"""

    def __init__(self, register):
        self._register = register

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
        current_value, ret = self._register.read_R(id)
        if ret != StatusCodeEnum.OK:
            return ret

        # 计算新值
        new_value = float(current_value) + float(step)

        # 写入新值
        ret = self._register.write_R(id, new_value)
        return ret

    def __getattr__(self, name):
        """代理其他方法到原始register对象"""
        return getattr(self._register, name)


# 初始化捷勃特机器人
arm = Arm()
# 连接捷勃特机器人
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 创建扩展的register对象
register_ext = RegisterExtension(arm.register)

# 先写入初始值
ret = register_ext.write_R(5, 8.6)
assert ret == StatusCodeEnum.OK

# 读取R寄存器
res, ret = register_ext.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"初始R寄存器值：{res}")

# 执行自增操作（默认自增1）
ret = register_ext.increment_R(5)
assert ret == StatusCodeEnum.OK

# 读取自增后的值
res, ret = register_ext.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"自增1后R寄存器值：{res}")

# 执行自增操作（自增2.5）
ret = register_ext.increment_R(5, step=2.5)
assert ret == StatusCodeEnum.OK

# 读取自增后的值
res, ret = register_ext.read_R(5)
assert ret == StatusCodeEnum.OK
print(f"自增2.5后R寄存器值：{res}")

# 删除R寄存器
ret = register_ext.delete_R(5)
assert ret == StatusCodeEnum.OK

# 断开捷勃特机器人连接
arm.disconnect()

