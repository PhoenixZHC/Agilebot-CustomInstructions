#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_classes import SerialParams
from Agilebot.IR.A.sdk_types import ModbusChannel

# 初始化Arm类
arm = Arm()
# 连接控制器
ret = arm.connect("10.27.1.254")
# 检查是否连接成功
assert ret == StatusCodeEnum.OK

# 设置modbus参数
params = SerialParams(channel=ModbusChannel.CONTROLLER_TCP_TO_485,ip='10.27.1.80',port=502)
id, ret_code = arm.modbus.set_parameter(params)
assert ret_code == StatusCodeEnum.OK

# 创建从站
slave = arm.modbus.get_slave(ModbusChannel.CONTROLLER_TCP_TO_485, 1, 1)

# 写入
value = [1,2,3,4]
assert slave.write_coils(0,value) == StatusCodeEnum.OK
assert slave.write_holding_regs(0,value) == StatusCodeEnum.OK

# 读取
res, ret = slave.read_coils(0,4)
assert ret == StatusCodeEnum.OK
print(f"读取的线圈值：{res}")
res, ret = slave.read_holding_regs(0,4)
assert ret == StatusCodeEnum.OK
print(f"读取的寄存器值：{res}")
res, ret = slave.read_input_regs(0,4)
assert ret == StatusCodeEnum.OK
print(f"读取的输入寄存器值：{res}")
res, ret = slave.read_discrete_inputs(0,4)
assert ret == StatusCodeEnum.OK
print(f"读取的离散输入值：{res}")

# 结束后断开机器人连接
arm.disconnect()
