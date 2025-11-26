#!python
# -*- coding: utf-8 -*-
"""
坐标系修改插件
提供指令：
1. SetTF - 工具坐标系（直接数值）
2. SetUF - 用户坐标系（直接数值）
3. SetTF_R - 工具坐标系（从R寄存器）
4. SetUF_R - 用户坐标系（从R寄存器）
5. SetTF_PR - 工具坐标系（从PR寄存器）
6. SetUF_PR - 用户坐标系（从PR寄存器）
"""

# 获取全局logger实例，只能在简单服务中使用
logger = globals().get('logger')
if logger is None:
    # 本地调试时，使用自带日志库
    import logging
    logger = logging.getLogger(__name__)

from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.extension import Extension
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.sdk_types import CoordinateSystemType

# 全局Arm对象，用于长连接
_global_arm = None


def _get_robot_ip():
    """
    获取机器人IP地址
    
    返回：
    - str: 机器人IP地址，失败返回None
    """
    try:
        extension = Extension()
        robot_ip = extension.get_robot_ip()
        return robot_ip
    except Exception as ex:
        logger.error(f"获取机器人IP失败: {ex}")
        return None


def _get_arm_connection():
    """
    获取Arm连接（长连接机制）
    如果未连接则连接，已连接则复用
    
    返回：
    - Arm: Arm对象，失败返回None
    - str: 错误信息，成功返回None
    """
    global _global_arm
    
    try:
        # 如果已有连接且连接状态正常，直接返回
        if _global_arm is not None:
            try:
                if _global_arm.is_connect():
                    return _global_arm, None
            except:
                # 连接状态检查失败，重置连接
                _global_arm = None
        
        # 创建新连接
        robot_ip = _get_robot_ip()
        if robot_ip is None:
            return None, "无法获取机器人IP地址"
        
        _global_arm = Arm()
        ret = _global_arm.connect(robot_ip)
        if ret != StatusCodeEnum.OK:
            _global_arm = None
            return None, f"连接机器人失败，错误代码：{ret}"
        
        return _global_arm, None
        
    except Exception as ex:
        logger.error(f"获取Arm连接失败: {ex}")
        _global_arm = None
        return None, f"获取连接失败：{str(ex)}"


def _get_param_name(param_index: int):
    """
    将参数编号转换为属性名
    
    参数：
    - param_index: 1-6 (1=X, 2=Y, 3=Z, 4=A/r, 5=B/p, 6=C/y)
    
    返回：
    - str: 属性名 ('x', 'y', 'z', 'r', 'p', 'y')
    """
    param_map = {
        1: 'x',  # X坐标
        2: 'y',  # Y坐标
        3: 'z',  # Z坐标
        4: 'r',  # 绕X轴旋转角度 (A -> r)
        5: 'p',  # 绕Y轴旋转角度 (B -> p)
        6: 'y'   # 绕Z轴旋转角度 (C -> y)
    }
    return param_map.get(param_index)


def SetTF(ID: int, Pos: int, Value: float) -> dict:
    """
    工具坐标系
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - Pos (int): 位置参数编号（1-6）
      - 1: X坐标（单位：mm）
      - 2: Y坐标（单位：mm）
      - 3: Z坐标（单位：mm）
      - 4: A角度（单位：度）
      - 5: B角度（单位：度）
      - 6: C角度（单位：度）
    - Value (float): 参数值（输入框输入，数值类型）
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证位置参数
    try:
        Pos = int(Pos)
    except (ValueError, TypeError):
        return {"success": False, "error": "位置参数必须是数值类型"}
    if Pos < 1 or Pos > 6:
        return {"success": False, "error": f"位置参数必须在1-6之间，当前值：{Pos}（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）"}
    
    param_attr = _get_param_name(Pos)
    if param_attr is None:
        return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}
    
    # 验证Value为数值类型
    try:
        Value = float(Value)
    except (ValueError, TypeError):
        return {"success": False, "error": f"无效的参数值：{Value}，必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.ToolFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 更新参数值（保留三位小数）
        Value = round(float(Value), 3)
        
        # 位置参数(1-3)更新到position，姿态参数(4-6)更新到orientation
        if Pos <= 3:
            # X, Y, Z 更新到 position
            setattr(coordinate.position, param_attr, Value)
        else:
            # R, P, Y 更新到 orientation
            if not hasattr(coordinate, 'orientation'):
                return {"success": False, "error": "坐标系对象没有orientation属性"}
            setattr(coordinate.orientation, param_attr, Value)
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.ToolFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"TF坐标系[{ID}]的{param_display}参数已更新为{Value}"
        }
        
    except Exception as ex:
        logger.error(f"SetTF执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def SetUF(ID: int, Pos: int, Value: float) -> dict:
    """
    用户坐标系
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - Pos (int): 位置参数编号（1-6）
      - 1: X坐标（单位：mm）
      - 2: Y坐标（单位：mm）
      - 3: Z坐标（单位：mm）
      - 4: A角度（单位：度）
      - 5: B角度（单位：度）
      - 6: C角度（单位：度）
    - Value (float): 参数值（输入框输入，数值类型）
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证位置参数
    try:
        Pos = int(Pos)
    except (ValueError, TypeError):
        return {"success": False, "error": "位置参数必须是数值类型"}
    if Pos < 1 or Pos > 6:
        return {"success": False, "error": f"位置参数必须在1-6之间，当前值：{Pos}（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）"}
    
    param_attr = _get_param_name(Pos)
    if param_attr is None:
        return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}
    
    # 验证Value为数值类型
    try:
        Value = float(Value)
    except (ValueError, TypeError):
        return {"success": False, "error": f"无效的参数值：{Value}，必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.UserFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 更新参数值（保留三位小数）
        Value = round(float(Value), 3)
        
        # 位置参数(1-3)更新到position，姿态参数(4-6)更新到orientation
        if Pos <= 3:
            # X, Y, Z 更新到 position
            setattr(coordinate.position, param_attr, Value)
        else:
            # R, P, Y 更新到 orientation
            if not hasattr(coordinate, 'orientation'):
                return {"success": False, "error": "坐标系对象没有orientation属性"}
            setattr(coordinate.orientation, param_attr, Value)
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.UserFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"UF坐标系[{ID}]的{param_display}参数已更新为{Value}"
        }
        
    except Exception as ex:
        logger.error(f"SetUF执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def SetTF_R(ID: int, Pos: int, R_ID: int) -> dict:
    """
    工具坐标系（从R寄存器读取值）
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - Pos (int): 位置参数编号（1-6）
      - 1: X坐标（单位：mm）
      - 2: Y坐标（单位：mm）
      - 3: Z坐标（单位：mm）
      - 4: A角度（单位：度）
      - 5: B角度（单位：度）
      - 6: C角度（单位：度）
    - R_ID (int): R寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证位置参数
    try:
        Pos = int(Pos)
    except (ValueError, TypeError):
        return {"success": False, "error": "位置参数必须是数值类型"}
    if Pos < 1 or Pos > 6:
        return {"success": False, "error": f"位置参数必须在1-6之间，当前值：{Pos}（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）"}
    
    param_attr = _get_param_name(Pos)
    if param_attr is None:
        return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}
    
    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 读取R寄存器
        r_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{ret}"}
        
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.ToolFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 更新参数值（保留三位小数）
        Value = round(float(r_value), 3)
        
        # 位置参数(1-3)更新到position，姿态参数(4-6)更新到orientation
        if Pos <= 3:
            # X, Y, Z 更新到 position
            setattr(coordinate.position, param_attr, Value)
        else:
            # R, P, Y 更新到 orientation
            if not hasattr(coordinate, 'orientation'):
                return {"success": False, "error": "坐标系对象没有orientation属性"}
            setattr(coordinate.orientation, param_attr, Value)
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.ToolFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"TF坐标系[{ID}]的{param_display}参数已从R寄存器[{R_ID}]更新为{Value}"
        }
        
    except Exception as ex:
        logger.error(f"SetTF_R执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def SetUF_R(ID: int, Pos: int, R_ID: int) -> dict:
    """
    用户坐标系（从R寄存器读取值）
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - Pos (int): 位置参数编号（1-6）
      - 1: X坐标（单位：mm）
      - 2: Y坐标（单位：mm）
      - 3: Z坐标（单位：mm）
      - 4: A角度（单位：度）
      - 5: B角度（单位：度）
      - 6: C角度（单位：度）
    - R_ID (int): R寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证位置参数
    try:
        Pos = int(Pos)
    except (ValueError, TypeError):
        return {"success": False, "error": "位置参数必须是数值类型"}
    if Pos < 1 or Pos > 6:
        return {"success": False, "error": f"位置参数必须在1-6之间，当前值：{Pos}（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）"}
    
    param_attr = _get_param_name(Pos)
    if param_attr is None:
        return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}
    
    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 读取R寄存器
        r_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{ret}"}
        
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.UserFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 更新参数值（保留三位小数）
        Value = round(float(r_value), 3)
        
        # 位置参数(1-3)更新到position，姿态参数(4-6)更新到orientation
        if Pos <= 3:
            # X, Y, Z 更新到 position
            setattr(coordinate.position, param_attr, Value)
        else:
            # R, P, Y 更新到 orientation
            if not hasattr(coordinate, 'orientation'):
                return {"success": False, "error": "坐标系对象没有orientation属性"}
            setattr(coordinate.orientation, param_attr, Value)
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.UserFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"UF坐标系[{ID}]的{param_display}参数已从R寄存器[{R_ID}]更新为{Value}"
        }
        
    except Exception as ex:
        logger.error(f"SetUF_R执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def SetTF_PR(ID: int, PR_ID: int) -> dict:
    """
    工具坐标系（从PR寄存器读取完整位姿）
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - PR_ID (int): PR寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证PR_ID为数值类型并转换为整数
    try:
        PR_ID = int(PR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "PR寄存器编号必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 读取PR寄存器
        pr_register, ret = arm.register.read_PR(PR_ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{ret}"}
        
        # 检查PR寄存器数据类型
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{PR_ID}]数据格式不正确，必须包含位姿数据"}
        
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.ToolFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
        # PR寄存器中的a/b/c对应坐标系中的r/p/y（绕X/Y/Z轴旋转角度）
        pr_position = pr_register.poseRegisterData.cartData.position
        # 更新位置信息
        coordinate.position.x = round(pr_position.x, 3)
        coordinate.position.y = round(pr_position.y, 3)
        coordinate.position.z = round(pr_position.z, 3)
        # 更新姿态信息：使用r/p/y（绕X/Y/Z轴旋转角度）
        # 检查是否有orientation属性（Rotation对象）
        if hasattr(coordinate, 'orientation'):
            coordinate.orientation.r = round(pr_position.a, 3)  # A -> r (绕X轴)
            coordinate.orientation.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
            coordinate.orientation.y = round(pr_position.c, 3)  # C -> y (绕Z轴)
        else:
            # 如果没有orientation，尝试在position对象上设置r/p/y
            coordinate.position.r = round(pr_position.a, 3)  # A -> r (绕X轴)
            coordinate.position.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
            # 注意：position.y是Y坐标，不能用于旋转角度
            # 如果position对象有yaw或其他属性用于绕Z轴旋转，使用它
            if hasattr(coordinate.position, 'yaw'):
                coordinate.position.yaw = round(pr_position.c, 3)
            elif hasattr(coordinate.position, 'rotation_z'):
                coordinate.position.rotation_z = round(pr_position.c, 3)
            else:
                # 如果都不存在，尝试设置c属性（可能SDK内部会映射）
                try:
                    setattr(coordinate.position, 'c', round(pr_position.c, 3))
                except:
                    logger.warning(f"无法设置绕Z轴旋转角度，请检查坐标系结构")
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.ToolFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        return {
            "success": True,
            "message": f"TF坐标系[{ID}]已从PR寄存器[{PR_ID}]更新：X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}, r={coordinate.position.r}, p={coordinate.position.p}, y={coordinate.position.y}"
        }
        
    except Exception as ex:
        logger.error(f"SetTF_PR执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def SetUF_PR(ID: int, PR_ID: int) -> dict:
    """
    用户坐标系（从PR寄存器读取完整位姿）
    
    参数：
    - ID (int): ID号（数值1-30，0是基础坐标系不可修改）
    - PR_ID (int): PR寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证ID为数值类型并转换为整数
    try:
        ID = int(ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ID号必须是数值类型"}
    if ID < 1 or ID > 30:
        return {"success": False, "error": f"ID号必须在1-30之间，当前值：{ID}"}
    
    # 验证PR_ID为数值类型并转换为整数
    try:
        PR_ID = int(PR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "PR寄存器编号必须是数值类型"}
    
    # 获取Arm连接（长连接机制）
    arm, error = _get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}
    
    try:
        # 读取PR寄存器
        pr_register, ret = arm.register.read_PR(PR_ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{ret}"}
        
        # 检查PR寄存器数据类型
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{PR_ID}]数据格式不正确，必须包含位姿数据"}
        
        # 获取现有坐标系
        coordinate, ret = arm.coordinate_system.get(CoordinateSystemType.UserFrame, ID)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
        
        # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
        # PR寄存器中的a/b/c对应坐标系中的r/p/y（绕X/Y/Z轴旋转角度）
        pr_position = pr_register.poseRegisterData.cartData.position
        # 更新位置信息
        coordinate.position.x = round(pr_position.x, 3)
        coordinate.position.y = round(pr_position.y, 3)
        coordinate.position.z = round(pr_position.z, 3)
        # 更新姿态信息：使用r/p/y（绕X/Y/Z轴旋转角度）
        # 检查是否有orientation属性（Rotation对象）
        if hasattr(coordinate, 'orientation'):
            coordinate.orientation.r = round(pr_position.a, 3)  # A -> r (绕X轴)
            coordinate.orientation.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
            coordinate.orientation.y = round(pr_position.c, 3)  # C -> y (绕Z轴)
        else:
            # 如果没有orientation，尝试在position对象上设置r/p/y
            coordinate.position.r = round(pr_position.a, 3)  # A -> r (绕X轴)
            coordinate.position.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
            # 注意：position.y是Y坐标，不能用于旋转角度
            # 如果position对象有yaw或其他属性用于绕Z轴旋转，使用它
            if hasattr(coordinate.position, 'yaw'):
                coordinate.position.yaw = round(pr_position.c, 3)
            elif hasattr(coordinate.position, 'rotation_z'):
                coordinate.position.rotation_z = round(pr_position.c, 3)
            else:
                # 如果都不存在，尝试设置c属性（可能SDK内部会映射）
                try:
                    setattr(coordinate.position, 'c', round(pr_position.c, 3))
                except:
                    logger.warning(f"无法设置绕Z轴旋转角度，请检查坐标系结构")
        
        # 更新坐标系
        ret = arm.coordinate_system.update(CoordinateSystemType.UserFrame, coordinate)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
        
        return {
            "success": True,
            "message": f"UF坐标系[{ID}]已从PR寄存器[{PR_ID}]更新：X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}, r={coordinate.position.r}, p={coordinate.position.p}, y={coordinate.position.y}"
        }
        
    except Exception as ex:
        logger.error(f"SetUF_PR执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}
