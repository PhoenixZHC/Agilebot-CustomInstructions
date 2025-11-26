#!python
# -*- coding: utf-8 -*-
"""
坐标系修改插件
提供两个指令：
1. 修改坐标系单个参数值（支持直接值和R寄存器）
2. 从PR寄存器读取值更新整个坐标系
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


def _get_coordinate_type(coord_type: str):
    """
    将字符串转换为坐标系类型枚举
    
    参数：
    - coord_type: "TF" 或 "UF"
    
    返回：
    - CoordinateSystemType 或 None
    """
    coord_type = coord_type.upper()
    if coord_type == "TF":
        return CoordinateSystemType.ToolFrame
    elif coord_type == "UF":
        return CoordinateSystemType.UserFrame
    else:
        return None


def _get_param_name(param_index: int):
    """
    将参数编号转换为属性名
    
    参数：
    - param_index: 1-6 (1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C)
    
    返回：
    - str: 属性名 ('x', 'y', 'z', 'a', 'b', 'c')
    """
    param_map = {
        1: 'x',
        2: 'y',
        3: 'z',
        4: 'a',
        5: 'b',
        6: 'c'
    }
    return param_map.get(param_index)


def update_coordinate_param(coord_type: str, coordinate_id: int, 
                           param_index: int, value: float) -> dict:
    """
    修改坐标系单个参数值（直接传值）
    
    参数：
    - coord_type (str): "TF" 或 "UF"，表示工具坐标系或用户坐标系
    - coordinate_id (int): 坐标系索引ID，范围1-30（0是基础坐标系不可修改）
    - param_index (int): 参数编号，1-6（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）
    - value (float): 要设置的值（坐标单位：mm，角度单位：度，精度：小数点后三位）
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    try:
        # 参数验证
        if coordinate_id < 1 or coordinate_id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{coordinate_id}"}
        
        if param_index < 1 or param_index > 6:
            return {"success": False, "error": f"参数编号必须在1-6之间，当前值：{param_index}"}
        
        # 获取坐标系类型
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF或UF"}
        
        # 获取参数属性名
        param_name = _get_param_name(param_index)
        if param_name is None:
            return {"success": False, "error": f"无效的参数编号：{param_index}"}
        
        # 获取机器人IP
        robot_ip = _get_robot_ip()
        if robot_ip is None:
            return {"success": False, "error": "无法获取机器人IP地址"}
        
        # 连接机器人
        arm = Arm()
        ret = arm.connect(robot_ip)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"连接机器人失败，错误代码：{ret}"}
        
        try:
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, coordinate_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新参数值（保留三位小数）
            value = round(value, 3)
            setattr(coordinate.position, param_name, value)
            
            # 更新坐标系
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
            return {
                "success": True, 
                "message": f"{coord_type}坐标系[{coordinate_id}]的{param_names[param_index]}参数已更新为{value}"
            }
            
        finally:
            # 断开连接
            arm.disconnect()
            
    except Exception as ex:
        logger.error(f"修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def update_coordinate_param_from_r(coord_type: str, coordinate_id: int, 
                                   param_index: int, r_id: int) -> dict:
    """
    修改坐标系单个参数值（从R寄存器读取）
    
    参数：
    - coord_type (str): "TF" 或 "UF"，表示工具坐标系或用户坐标系
    - coordinate_id (int): 坐标系索引ID，范围1-30（0是基础坐标系不可修改）
    - param_index (int): 参数编号，1-6（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）
    - r_id (int): R寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    try:
        # 参数验证
        if coordinate_id < 1 or coordinate_id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{coordinate_id}"}
        
        if param_index < 1 or param_index > 6:
            return {"success": False, "error": f"参数编号必须在1-6之间，当前值：{param_index}"}
        
        # 获取坐标系类型
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF或UF"}
        
        # 获取参数属性名
        param_name = _get_param_name(param_index)
        if param_name is None:
            return {"success": False, "error": f"无效的参数编号：{param_index}"}
        
        # 获取机器人IP
        robot_ip = _get_robot_ip()
        if robot_ip is None:
            return {"success": False, "error": "无法获取机器人IP地址"}
        
        # 连接机器人
        arm = Arm()
        ret = arm.connect(robot_ip)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"连接机器人失败，错误代码：{ret}"}
        
        try:
            # 读取R寄存器
            r_value, ret = arm.register.read_R(r_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取R寄存器[{r_id}]失败，错误代码：{ret}"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, coordinate_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新参数值（保留三位小数）
            value = round(r_value, 3)
            setattr(coordinate.position, param_name, value)
            
            # 更新坐标系
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
            return {
                "success": True, 
                "message": f"{coord_type}坐标系[{coordinate_id}]的{param_names[param_index]}参数已从R寄存器[{r_id}]更新为{value}"
            }
            
        finally:
            # 断开连接
            arm.disconnect()
            
    except Exception as ex:
        logger.error(f"从R寄存器修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def update_coordinate_from_pr(coord_type: str, coordinate_id: int, pr_id: int) -> dict:
    """
    从PR寄存器读取值更新整个坐标系
    
    参数：
    - coord_type (str): "TF" 或 "UF"，表示工具坐标系或用户坐标系
    - coordinate_id (int): 坐标系索引ID，范围1-30（0是基础坐标系不可修改）
    - pr_id (int): PR寄存器编号
    
    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    try:
        # 参数验证
        if coordinate_id < 1 or coordinate_id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{coordinate_id}"}
        
        # 获取坐标系类型
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF或UF"}
        
        # 获取机器人IP
        robot_ip = _get_robot_ip()
        if robot_ip is None:
            return {"success": False, "error": "无法获取机器人IP地址"}
        
        # 连接机器人
        arm = Arm()
        ret = arm.connect(robot_ip)
        if ret != StatusCodeEnum.OK:
            return {"success": False, "error": f"连接机器人失败，错误代码：{ret}"}
        
        try:
            # 读取PR寄存器
            pr_register, ret = arm.register.read_PR(pr_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取PR寄存器[{pr_id}]失败，错误代码：{ret}"}
            
            # 检查PR寄存器数据类型
            if not hasattr(pr_register, 'poseRegisterData') or \
               not hasattr(pr_register.poseRegisterData, 'cartData') or \
               not hasattr(pr_register.poseRegisterData.cartData, 'position'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，必须包含位姿数据"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, coordinate_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
            pr_position = pr_register.poseRegisterData.cartData.position
            coordinate.position.x = round(pr_position.x, 3)
            coordinate.position.y = round(pr_position.y, 3)
            coordinate.position.z = round(pr_position.z, 3)
            coordinate.position.a = round(pr_position.a, 3)
            coordinate.position.b = round(pr_position.b, 3)
            coordinate.position.c = round(pr_position.c, 3)
            
            # 更新坐标系
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            return {
                "success": True,
                "message": f"{coord_type}坐标系[{coordinate_id}]已从PR寄存器[{pr_id}]更新：X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}, A={coordinate.position.a}, B={coordinate.position.b}, C={coordinate.position.c}"
            }
            
        finally:
            # 断开连接
            arm.disconnect()
            
    except Exception as ex:
        logger.error(f"从PR寄存器更新坐标系失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}
