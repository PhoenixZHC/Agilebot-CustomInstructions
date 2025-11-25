#!python
# -*- coding: utf-8 -*-
"""
坐标系修改插件 - CM

新架构功能（分层结构）：
第一层：选择坐标系类型
  - SetTF  - 工具坐标系（Tool Frame）
  - SetUF  - 用户坐标系（User Frame）

第二层：选择输入方式
  数值输入：
    - SetTF(id, x, y, z, a, b, c)      - 直接输入XYZABC值
    - SetTFR(id, param_name, r_id)     - 从R寄存器输入（param_name: X/Y/Z/A/B/C）
    - SetUF(id, x, y, z, a, b, c)      - 直接输入XYZABC值
    - SetUFR(id, param_name, r_id)     - 从R寄存器输入（param_name: X/Y/Z/A/B/C）
  PR位姿寄存器：
    - SetTFPR(id, pr_id)               - 从PR寄存器读取完整XYZABC值
    - SetUFPR(id, pr_id)               - 从PR寄存器读取完整XYZABC值

使用示例（无括号格式）：
  CALL_SERVICE CM SetTF1,100.000,200.000,300.000,1.000,2.000,3.000
  CALL_SERVICE CM SetTF1,X,R5
  CALL_SERVICE CM SetTF1,PR5
  CALL_SERVICE CM SetUF1,100.000,200.000,300.000,1.000,2.000,3.000
  CALL_SERVICE CM SetUF1,X,R5
  CALL_SERVICE CM SetUF1,PR5
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

# 全局变量：保存机器人连接（长连接）
_arm_connection = None
_robot_ip = None


def _get_robot_ip():
    """获取机器人IP地址"""
    global _robot_ip
    if _robot_ip is None:
        try:
            extension = Extension()
            _robot_ip = extension.get_robot_ip()
        except Exception as ex:
            logger.error(f"获取机器人IP失败: {ex}")
    return _robot_ip


def _get_arm_connection():
    """获取机器人连接（长连接，复用连接，自动重连）"""
    global _arm_connection, _robot_ip
    
    # 如果连接不存在，创建新连接
    if _arm_connection is None:
        robot_ip = _get_robot_ip()
        if robot_ip is None:
            return None
        
        try:
            _arm_connection = Arm()
            ret = _arm_connection.connect(robot_ip)
            if ret != StatusCodeEnum.OK:
                logger.error(f"连接机器人失败，错误代码：{ret}")
                _arm_connection = None
                return None
            logger.info(f"机器人连接成功，IP: {robot_ip}")
        except Exception as ex:
            logger.error(f"创建机器人连接失败: {ex}")
            _arm_connection = None
            return None
    else:
        # 检查连接状态，如果已断开则重新连接
        try:
            is_connected = _arm_connection.is_connect()
            if not is_connected:
                logger.warning("检测到连接已断开，尝试重新连接...")
                robot_ip = _get_robot_ip()
                if robot_ip is None:
                    _arm_connection = None
                    return None
                
                # 尝试重新连接
                try:
                    ret = _arm_connection.connect(robot_ip)
                    if ret != StatusCodeEnum.OK:
                        logger.error(f"重新连接机器人失败，错误代码：{ret}")
                        _arm_connection = None
                        return None
                    logger.info(f"机器人重新连接成功，IP: {robot_ip}")
                except Exception as ex:
                    logger.error(f"重新连接机器人失败: {ex}")
                    _arm_connection = None
                    return None
        except Exception as ex:
            # 如果检查连接状态时出错，说明连接可能已断开，尝试重新连接
            logger.warning(f"检查连接状态时出错: {ex}，尝试重新连接...")
            try:
                _arm_connection.disconnect()
            except:
                pass
            _arm_connection = None
            
            # 重新创建连接
            robot_ip = _get_robot_ip()
            if robot_ip is None:
                return None
            
            try:
                _arm_connection = Arm()
                ret = _arm_connection.connect(robot_ip)
                if ret != StatusCodeEnum.OK:
                    logger.error(f"重新连接机器人失败，错误代码：{ret}")
                    _arm_connection = None
                    return None
                logger.info(f"机器人重新连接成功，IP: {robot_ip}")
            except Exception as ex:
                logger.error(f"重新连接机器人失败: {ex}")
                _arm_connection = None
                return None
    
    return _arm_connection


def _get_coordinate_type(coord_type):
    """
    将字符串或数值转换为坐标系类型枚举
    支持：1=TF, 2=UF 或 "TF"/"UF"
    """
    # 如果是数值，转换为字符串
    if isinstance(coord_type, (int, float)):
        if coord_type == 1:
            return CoordinateSystemType.ToolFrame
        elif coord_type == 2:
            return CoordinateSystemType.UserFrame
        else:
            return None
    
    # 如果是字符串，转换为大写后判断
    coord_type = str(coord_type).upper()
    if coord_type == "TF" or coord_type == "1":
        return CoordinateSystemType.ToolFrame
    elif coord_type == "UF" or coord_type == "2":
        return CoordinateSystemType.UserFrame
    else:
        return None


def _get_param_name(param_index: int):
    """将参数编号转换为属性名（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）"""
    param_map = {
        1: 'x',
        2: 'y',
        3: 'z',
        4: 'a',
        5: 'b',
        6: 'c'
    }
    return param_map.get(param_index)


def _get_param_name_from_string(param_name: str):
    """
    将参数名字符串转换为属性名和参数索引
    支持："X"/"x" -> ('x', 1), "Y"/"y" -> ('y', 2), "Z"/"z" -> ('z', 3)
         "A"/"a" -> ('a', 4), "B"/"b" -> ('b', 5), "C"/"c" -> ('c', 6)
    """
    param_name = str(param_name).upper()
    param_map = {
        'X': ('x', 1),
        'Y': ('y', 2),
        'Z': ('z', 3),
        'A': ('a', 4),
        'B': ('b', 5),
        'C': ('c', 6)
    }
    return param_map.get(param_name)


# ==================== 新架构：分层函数结构 ====================

def SetTF(id, x, y, z, a, b, c):
    """修改工具坐标系参数值"""
    return _set_coordinate_direct(CoordinateSystemType.ToolFrame, id, x, y, z, a, b, c)


def SetUF(id, x, y, z, a, b, c):
    """修改用户坐标系参数值"""
    return _set_coordinate_direct(CoordinateSystemType.UserFrame, id, x, y, z, a, b, c)


def SetTFR(id, param_name, r_register):
    """从R寄存器修改工具坐标系单个参数"""
    # 解析R寄存器编号（支持"R5"或5格式）
    if isinstance(r_register, str):
        r_register = r_register.upper().strip()
        if r_register.startswith('R'):
            r_id = int(r_register[1:])
        else:
            r_id = int(r_register)
    else:
        r_id = int(r_register)
    return _set_coordinate_from_r(CoordinateSystemType.ToolFrame, id, param_name, r_id)


def SetUFR(id, param_name, r_register):
    """从R寄存器修改用户坐标系单个参数"""
    # 解析R寄存器编号（支持"R5"或5格式）
    if isinstance(r_register, str):
        r_register = r_register.upper().strip()
        if r_register.startswith('R'):
            r_id = int(r_register[1:])
        else:
            r_id = int(r_register)
    else:
        r_id = int(r_register)
    return _set_coordinate_from_r(CoordinateSystemType.UserFrame, id, param_name, r_id)


def SetTFPR(id, pr_register):
    """从PR寄存器更新工具坐标系"""
    # 解析PR寄存器编号（支持"PR5"或5格式）
    if isinstance(pr_register, str):
        pr_register = pr_register.upper().strip()
        if pr_register.startswith('PR'):
            pr_id = int(pr_register[2:])
        else:
            pr_id = int(pr_register)
    else:
        pr_id = int(pr_register)
    return _set_coordinate_from_pr(CoordinateSystemType.ToolFrame, id, pr_id)


def SetUFPR(id, pr_register):
    """从PR寄存器更新用户坐标系"""
    # 解析PR寄存器编号（支持"PR5"或5格式）
    if isinstance(pr_register, str):
        pr_register = pr_register.upper().strip()
        if pr_register.startswith('PR'):
            pr_id = int(pr_register[2:])
        else:
            pr_id = int(pr_register)
    else:
        pr_id = int(pr_register)
    return _set_coordinate_from_pr(CoordinateSystemType.UserFrame, id, pr_id)


# ==================== 内部辅助函数 ====================

def _set_coordinate_direct(sys_type: CoordinateSystemType, id: int, x: float, y: float, z: float, a: float, b: float, c: float) -> dict:
    """
    修改坐标系参数值（直接传值）- 内部辅助函数
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        # 验证参数值（确保是数字）
        try:
            x = float(x)
            y = float(y)
            z = float(z)
            a = float(a)
            b = float(b)
            c = float(c)
        except (ValueError, TypeError) as ex:
            return {"success": False, "error": f"参数值必须是数字，错误：{str(ex)}"}
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新位置值（X, Y, Z）- 保留三位小数
            coordinate.position.x = round(x, 3)
            coordinate.position.y = round(y, 3)
            coordinate.position.z = round(z, 3)
            
            # 更新角度值（A, B, C）- 写入到orientation (r, p, y)
            if hasattr(coordinate, 'orientation'):
                coordinate.orientation.r = round(a, 3)  # A -> r (绕X轴)
                coordinate.orientation.p = round(b, 3)  # B -> p (绕Y轴)
                coordinate.orientation.y = round(c, 3)  # C -> y (绕Z轴)
            else:
                return {"success": False, "error": f"TF/UF坐标系缺少orientation属性，无法设置角度值"}
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            return {
                "success": True, 
                "message": f"{coord_type_name}坐标系[{id}]已更新：X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}, R={coordinate.orientation.r}, P={coordinate.orientation.p}, Y={coordinate.orientation.y}"
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def _set_coordinate_from_r(sys_type: CoordinateSystemType, id: int, param_name: str, r_id: int) -> dict:
    """
    修改坐标系单个参数值（从R寄存器读取）- 内部辅助函数
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        # 转换参数名为属性名
        param_info = _get_param_name_from_string(param_name)
        if param_info is None:
            return {"success": False, "error": f"无效的参数名称：{param_name}，必须是X/Y/Z/A/B/C之一"}
        
        attr_name, param_index = param_info
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 读取R寄存器
            r_value, ret = arm.register.read_R(r_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取R寄存器[{r_id}]失败，错误代码：{ret}"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新参数值（保留三位小数）
            value = round(r_value, 3)
            
            # 根据参数类型设置position或orientation
            if attr_name in ['x', 'y', 'z']:
                setattr(coordinate.position, attr_name, value)
            elif attr_name in ['a', 'b', 'c']:
                # 映射到orientation的r, p, y
                orientation_map = {'a': 'r', 'b': 'p', 'c': 'y'}
                if hasattr(coordinate, 'orientation') and hasattr(coordinate.orientation, orientation_map[attr_name]):
                    setattr(coordinate.orientation, orientation_map[attr_name], value)
                else:
                    return {"success": False, "error": f"坐标系不支持{param_name}角度属性，无法设置"}
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            return {
                "success": True, 
                "message": f"{coord_type_name}坐标系[{id}]的{param_name}参数已从R寄存器[{r_id}]更新为{value}"
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"从R寄存器修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def _set_coordinate_from_pr(sys_type: CoordinateSystemType, id: int, pr_id: int) -> dict:
    """
    从PR寄存器读取值更新整个坐标系 - 内部辅助函数
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 读取PR寄存器
            pr_register, ret = arm.register.read_PR(pr_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取PR寄存器[{pr_id}]失败，错误代码：{ret}"}
            
            # 检查PR寄存器数据格式
            if not hasattr(pr_register, 'poseRegisterData'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少poseRegisterData属性"}
            
            if not hasattr(pr_register.poseRegisterData, 'cartData'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少cartData属性，请确保PR寄存器包含笛卡尔坐标数据"}
            
            if not hasattr(pr_register.poseRegisterData.cartData, 'position'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少position属性"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
            pr_position = pr_register.poseRegisterData.cartData.position
            
            try:
                # 读取位置值（X, Y, Z）
                coordinate.position.x = round(pr_position.x, 3)
                coordinate.position.y = round(pr_position.y, 3)
                coordinate.position.z = round(pr_position.z, 3)
                
                # 读取角度值（A, B, C）- 写入到orientation (r, p, y)
                if hasattr(coordinate, 'orientation'):
                    coordinate.orientation.r = round(pr_position.a, 3)  # A -> r (绕X轴)
                    coordinate.orientation.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
                    coordinate.orientation.y = round(pr_position.c, 3)  # C -> y (绕Z轴)
                else:
                    return {"success": False, "error": f"TF/UF坐标系缺少orientation属性，无法设置角度值"}
                    
            except AttributeError as attr_ex:
                missing_attr = str(attr_ex).split("'")[1] if "'" in str(attr_ex) else "未知属性"
                error_msg = f"访问属性失败：{missing_attr}"
                
                if 'coordinate' in str(attr_ex) or 'orientation' in str(attr_ex):
                    error_msg += f"。TF/UF坐标系可能缺少{missing_attr}属性，请检查坐标系数据结构"
                else:
                    error_msg += f"。PR寄存器[{pr_id}]可能缺少{missing_attr}属性，请确保PR寄存器包含完整的XYZABC数据"
                
                return {"success": False, "error": error_msg}
            except Exception as ex:
                return {"success": False, "error": f"读取或写入XYZABC值时出错：{str(ex)}"}
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            
            msg = f"{coord_type_name}坐标系[{id}]已从PR寄存器[{pr_id}]更新："
            msg += f"X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}"
            
            if hasattr(coordinate, 'orientation'):
                msg += f", R={coordinate.orientation.r}, P={coordinate.orientation.p}, Y={coordinate.orientation.y}"
                msg += "（A->R, B->P, C->Y）"
            else:
                msg += "（注意：角度值可能未更新）"
            
            return {
                "success": True,
                "message": msg
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"从PR寄存器更新坐标系失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


# ==================== 旧函数（保留兼容性，但建议使用新函数） ====================

def Set_coord(coord_type, id, x, y, z, a, b, c):
    """
    修改坐标系参数值（直接传值）
    
    参数（位置参数，按顺序）：
    1. coord_type: "TF"或"UF"（工具坐标系/用户坐标系，只能是字符串）
    2. id: 坐标系ID（1-30）
    3. x: X坐标值（单位：mm）
    4. y: Y坐标值（单位：mm）
    5. z: Z坐标值（单位：mm）
    6. a: A角度值（单位：度）
    7. b: B角度值（单位：度）
    8. c: C角度值（单位：度）
    
    使用：CALL_SERVICE CM Set_coord(TF,1,100.0,200.0,300.0,0.0,0.0,0.0)
    说明：参数按位置传递，第一个参数是坐标系类型（TF/UF），第二个是坐标系ID，后面6个是XYZABC值
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        # 验证坐标系类型（只能是TF或UF字符串）
        coord_type = str(coord_type).upper()
        if coord_type not in ["TF", "UF"]:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF或UF"}
        
        # 转换坐标系类型
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF或UF"}
        
        # 验证参数值（确保是数字）
        try:
            x = float(x)
            y = float(y)
            z = float(z)
            a = float(a)
            b = float(b)
            c = float(c)
        except (ValueError, TypeError) as ex:
            return {"success": False, "error": f"参数值必须是数字，错误：{str(ex)}"}
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新位置值（X, Y, Z）- 保留三位小数
            coordinate.position.x = round(x, 3)
            coordinate.position.y = round(y, 3)
            coordinate.position.z = round(z, 3)
            
            # 更新角度值（A, B, C）- 写入到orientation (r, p, y)
            if hasattr(coordinate, 'orientation'):
                coordinate.orientation.r = round(a, 3)  # A -> r (绕X轴)
                coordinate.orientation.p = round(b, 3)  # B -> p (绕Y轴)
                coordinate.orientation.y = round(c, 3)  # C -> y (绕Z轴)
            else:
                return {"success": False, "error": f"TF/UF坐标系缺少orientation属性，无法设置角度值"}
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            return {
                "success": True, 
                "message": f"{coord_type_name}坐标系[{id}]已更新：X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}, R={coordinate.orientation.r}, P={coordinate.orientation.p}, Y={coordinate.orientation.y}"
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def Set_coord_r(coord_type, id, param_id, r_id):
    """
    修改坐标系单个参数值（从R寄存器读取）
    
    参数（位置参数，按顺序）：
    1. coord_type: "TF"/"UF"或1/2（1=TF工具坐标系, 2=UF用户坐标系）
    2. id: 坐标系ID（1-30）
    3. param_id: 参数编号（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）
    4. r_id: R寄存器编号
    
    使用：CALL_SERVICE CM Set_coord_r(1,1,1,5)
    说明：参数按位置传递，第一个参数是坐标系类型，第二个是坐标系ID，第三个是参数编号，第四个是R寄存器编号
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        if param_id < 1 or param_id > 6:
            return {"success": False, "error": f"参数编号必须在1-6之间，当前值：{param_id}"}
        
        # 转换坐标系类型（支持1=TF, 2=UF）
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF/UF或1/2（1=TF, 2=UF）"}
        
        # 转换参数编号为属性名
        param_name = _get_param_name(param_id)
        if param_name is None:
            return {"success": False, "error": f"无效的参数编号：{param_id}"}
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 读取R寄存器
            r_value, ret = arm.register.read_R(r_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取R寄存器[{r_id}]失败，错误代码：{ret}"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 更新参数值（保留三位小数）
            value = round(r_value, 3)
            setattr(coordinate.position, param_name, value)
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            return {
                "success": True, 
                "message": f"{coord_type_name}坐标系[{id}]的{param_names[param_id]}参数已从R寄存器[{r_id}]更新为{value}"
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"从R寄存器修改坐标系参数失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


def Set_coord_pr(coord_type, id, pr_id):
    """
    从PR寄存器读取值更新整个坐标系
    
    参数（位置参数，按顺序）：
    1. coord_type: "TF"/"UF"或1/2（1=TF工具坐标系, 2=UF用户坐标系）
    2. id: 坐标系ID（1-30）
    3. pr_id: PR寄存器编号（读取完整的XYZABC值）
    
    使用：CALL_SERVICE CM Set_coord_pr(1,1,5)
    说明：参数按位置传递，第一个参数是坐标系类型，第二个是坐标系ID，第三个是PR寄存器编号
    """
    try:
        # 参数验证
        if id < 1 or id > 30:
            return {"success": False, "error": f"坐标系索引ID必须在1-30之间，当前值：{id}"}
        
        # 转换坐标系类型（支持1=TF, 2=UF）
        sys_type = _get_coordinate_type(coord_type)
        if sys_type is None:
            return {"success": False, "error": f"无效的坐标系类型：{coord_type}，必须是TF/UF或1/2（1=TF, 2=UF）"}
        
        # 获取机器人连接（长连接）
        arm = _get_arm_connection()
        if arm is None:
            return {"success": False, "error": "无法获取机器人连接"}
        
        try:
            # 读取PR寄存器
            pr_register, ret = arm.register.read_PR(pr_id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"读取PR寄存器[{pr_id}]失败，错误代码：{ret}"}
            
            # 检查PR寄存器数据格式（检查大小写正确的属性名）
            if not hasattr(pr_register, 'poseRegisterData'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少poseRegisterData属性"}
            
            if not hasattr(pr_register.poseRegisterData, 'cartData'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少cartData属性，请确保PR寄存器包含笛卡尔坐标数据"}
            
            if not hasattr(pr_register.poseRegisterData.cartData, 'position'):
                return {"success": False, "error": f"PR寄存器[{pr_id}]数据格式不正确，缺少position属性"}
            
            # 获取现有坐标系
            coordinate, ret = arm.coordinate_system.get(sys_type, id)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"获取坐标系失败，错误代码：{ret}"}
            
            # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
            # PR寄存器路径：pr_register.poseRegisterData.cartData.position (x, y, z, a, b, c)
            # TF/UF坐标系路径：
            #   - coordinate.position (x, y, z) - Translation
            #   - coordinate.orientation (r, p, y) - Rotation
            # 注意：PR使用a/b/c，TF/UF使用orientation.r/p/y
            pr_position = pr_register.poseRegisterData.cartData.position
            
            # 直接读取X, Y, Z, A, B, C值并写入坐标系
            try:
                # 读取位置值（X, Y, Z）- 写入到coordinate.position
                coordinate.position.x = round(pr_position.x, 3)
                coordinate.position.y = round(pr_position.y, 3)
                coordinate.position.z = round(pr_position.z, 3)
                
                # 读取角度值（A, B, C）- 写入到coordinate.orientation (r, p, y)
                # PR的A/B/C对应TF/UF的orientation.r/p/y
                # 根据文档：r=绕X轴旋转, p=绕Y轴旋转, y=绕Z轴旋转
                # PR的a/b/c也是绕X/Y/Z轴旋转，所以直接映射：a->r, b->p, c->y
                if hasattr(coordinate, 'orientation'):
                    coordinate.orientation.r = round(pr_position.a, 3)  # A -> r (绕X轴)
                    coordinate.orientation.p = round(pr_position.b, 3)  # B -> p (绕Y轴)
                    coordinate.orientation.y = round(pr_position.c, 3)  # C -> y (绕Z轴)
                else:
                    return {"success": False, "error": f"TF/UF坐标系缺少orientation属性，无法设置角度值"}
                    
            except AttributeError as attr_ex:
                # 如果缺少某个属性，返回详细错误
                missing_attr = str(attr_ex).split("'")[1] if "'" in str(attr_ex) else "未知属性"
                error_msg = f"访问属性失败：{missing_attr}"
                
                # 检查是PR寄存器缺少属性还是坐标系缺少属性
                if 'coordinate' in str(attr_ex) or 'orientation' in str(attr_ex):
                    error_msg += f"。TF/UF坐标系可能缺少{missing_attr}属性，请检查坐标系数据结构"
                else:
                    error_msg += f"。PR寄存器[{pr_id}]可能缺少{missing_attr}属性，请确保PR寄存器包含完整的XYZABC数据"
                
                return {"success": False, "error": error_msg}
            except Exception as ex:
                return {"success": False, "error": f"读取或写入XYZABC值时出错：{str(ex)}"}
            
            # 保存更新
            ret = arm.coordinate_system.update(sys_type, coordinate)
            if ret != StatusCodeEnum.OK:
                return {"success": False, "error": f"更新坐标系失败，错误代码：{ret}"}
            
            # 返回成功信息
            coord_type_name = "TF" if sys_type == CoordinateSystemType.ToolFrame else "UF"
            
            # 构建返回消息
            msg = f"{coord_type_name}坐标系[{id}]已从PR寄存器[{pr_id}]更新："
            msg += f"X={coordinate.position.x}, Y={coordinate.position.y}, Z={coordinate.position.z}"
            
            if hasattr(coordinate, 'orientation'):
                msg += f", R={coordinate.orientation.r}, P={coordinate.orientation.p}, Y={coordinate.orientation.y}"
                msg += "（A->R, B->P, C->Y）"
            else:
                msg += "（注意：角度值可能未更新）"
            
            return {
                "success": True,
                "message": msg
            }
            
        except Exception as ex:
            # 如果操作出错，检查是否是连接问题
            error_msg = str(ex).lower()
            if 'connect' in error_msg or 'connection' in error_msg or '网络' in error_msg or '远程' in error_msg:
                # 连接相关错误，重置连接以便下次重连
                global _arm_connection
                logger.error(f"连接错误，重置连接: {ex}")
                if _arm_connection is not None:
                    try:
                        _arm_connection.disconnect()
                    except:
                        pass
                _arm_connection = None
            raise
            
    except Exception as ex:
        logger.error(f"从PR寄存器更新坐标系失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}

