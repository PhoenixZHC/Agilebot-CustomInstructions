#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: modbus使用示例 / Example of modbus usage
"""
from Agilebot import Arm, ModbusChannel, SerialParams, StatusCodeEnum

# [ZH] 初始化Arm类
# [EN] Initialize the robot
arm = Arm()
# [ZH] 连接控制器
# [EN] Connect to the robot
ret = arm.connect("10.27.1.254")
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 设置modbus参数
# [EN] Set Modbus parameters
params = SerialParams(channel=ModbusChannel.CONTROLLER_TCP_TO_485, ip="10.27.1.80", port=502)
id, ret_code = arm.modbus.set_parameter(params)
if ret_code == StatusCodeEnum.OK:
    print("设置Modbus参数成功 / Set Modbus parameters successfully")
else:
    print(f"设置Modbus参数失败，错误代码 / Set Modbus parameters failed, error code: {ret_code.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 创建从站
# [EN] Create a slave
slave = arm.modbus.get_slave(ModbusChannel.CONTROLLER_TCP_TO_485, 1, 1)

# [ZH] 写入
# [EN] Write to registers
value = [1, 2, 3, 4]
ret = slave.write_coils(0, value)
if ret == StatusCodeEnum.OK:
    print("写入线圈成功 / Write coils successfully")
else:
    print(f"写入线圈失败，错误代码 / Write coils failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

ret = slave.write_holding_regs(0, value)
if ret == StatusCodeEnum.OK:
    print("写入保持寄存器成功 / Write holding registers successfully")
else:
    print(f"写入保持寄存器失败，错误代码 / Write holding registers failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 读取
# [EN] Read registers
res, ret = slave.read_coils(0, 4)
if ret == StatusCodeEnum.OK:
    print("读取线圈成功 / Read coils successfully")
    print(f"读取的线圈值 / Read coil values：{res}")
else:
    print(f"读取线圈失败，错误代码 / Read coils failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

res, ret = slave.read_holding_regs(0, 4)
if ret == StatusCodeEnum.OK:
    print("读取保持寄存器成功 / Read holding registers successfully")
    print(f"读取的寄存器值 / Read register values：{res}")
else:
    print(f"读取保持寄存器失败，错误代码 / Read holding registers failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

res, ret = slave.read_input_regs(0, 4)
if ret == StatusCodeEnum.OK:
    print("读取输入寄存器成功 / Read input registers successfully")
    print(f"读取的输入寄存器值 / Read input register values：{res}")
else:
    print(f"读取输入寄存器失败，错误代码 / Read input registers failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

res, ret = slave.read_discrete_inputs(0, 4)
if ret == StatusCodeEnum.OK:
    print("读取离散输入成功 / Read discrete inputs successfully")
    print(f"读取的离散输入值 / Read discrete input values：{res}")
else:
    print(f"读取离散输入失败，错误代码 / Read discrete inputs failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 结束后断开机器人连接
# [EN] Disconnect from the robot
arm.disconnect()
print("机器人断开连接成功 / Robot disconnected successfully")
