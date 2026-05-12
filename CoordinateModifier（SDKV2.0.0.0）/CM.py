#!python
# -*- coding: utf-8 -*-
"""
**CM (Custom Module)** 用户自定义指令插件
版本 V1.4.1 | 更新日期：2026年5月12日
**验证基准：** 机器人控制软件 **7.8.B.0**；其它版本可能不兼容，部署前请自测。
功能说明：
本插件实现以下功能：坐标系（TF/UF）参数设置与从R/PR读取设置；
R寄存器自增/自减；
字符串数据拆解（Strp）写入PR；
工具坐标系视觉补正（TFShift）；
十进制到十六进制转换（DecToHex）；
以及回转标记在 `turnCircle` 与单个R之间的同步（TurnCountToR / RToTurnCount，单轴替换，`Joint_ID` 指定 J1~J6）。


提供指令：
1. SetTF - 工具坐标系（直接数值）
2. SetUF - 用户坐标系（直接数值）
3. SetTF_R - 工具坐标系（从R寄存器）
4. SetUF_R - 用户坐标系（从R寄存器）
5. SetTF_PR - 工具坐标系（从PR寄存器）
6. SetUF_PR - 用户坐标系（从PR寄存器）
7. Incr - R寄存器自增
8. Decr - R寄存器自减
9. Strp - 拆解字符串数据到PR寄存器
10. TFShift - 工具坐标系补正（基于视觉反馈）
11. DecToHex - 从十进制转换为十六进制
12. TurnCountToR - 将PR位姿回转数写入R寄存器（单轴）
13. RToTurnCount - 将R寄存器回写到PR位姿回转数（单轴）

连接诊断文件（示教器「日志」窗口可能无 Python 输出）：会依次尝试
环境变量 AGILEBOT_CM_LOG_FILE、系统临时目录、当前工作目录、本文件所在目录、/tmp 等路径下的 agilebot_cm_plugin.log 。

Arm 与官方 Python_v2.0.0.0/example 中 `Arm()` + `connect(IP)` 流程一致。
未设置 AGILEBOT_ARM_LOCAL_PROXY 时：仅在 CPU 为 x86_64/amd64 时默认 Arm(local_proxy=True)
（与 AGILEBOT_ARM_LOCAL_PROXY=true 一致，便于 PC 侧扩展服务）；示教器等 ARM 环境默认
Arm(local_proxy=False)，避免启动 SDK 自带的 linux_amd64 本机代理二进制导致 Exec format error。
任意架构均可显式设 true/false 覆盖。

**与 Python SDK 2.0.1.0 更新说明对齐：**本插件已使用 `is_connected()`；为兼容仍带
`is_connect()` 的 2.0.0.x 运行库，长连接复用处会优先 `is_connected` 再回退 `is_connect`。
`get_version` 已更名为 `get_controller_version`（本插件未直接调用）。底层通讯与本地
proxy 行为以所安装 Agilebot 包版本为准。

ARM 示教器上若未配置示教器 IP，会尝试将「本机检测到的 IPv4」作为 `connect` 第二参数
（见 `__resolve_robot_and_teach_ips`）；可用 `AGILEBOT_AUTO_TEACH_IP_ON_ARM=0` 关闭，
用 `AGILEBOT_TEACH_PANEL_IP` 手动指定更准确。

"""

import logging

# NOTE: stdout fallback logger logic is inlined into _LoggerAdapter.__init__
# to avoid Cursor symbol suggestions for a helper function.


class _LoggerAdapter:
    """统一日志入口，兼容宿主logger并强制stdout兜底输出。"""

    def __init__(self, host_logger):
        self._host_logger = host_logger
        py_logger = logging.getLogger(__name__)
        if not py_logger.handlers:
            _handler = logging.StreamHandler()
            _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
            py_logger.addHandler(_handler)
        py_logger.setLevel(logging.INFO)
        self._py_logger = py_logger
        if hasattr(self._host_logger, "setLevel"):
            try:
                self._host_logger.setLevel(logging.INFO)
            except Exception:
                pass

    def _render(self, msg, args):
        rendered = str(msg)
        if args:
            try:
                rendered = rendered % args
            except Exception:
                pass
        return rendered

    def _call_host(self, level_name, msg, args, kwargs):
        if self._host_logger is None:
            return
        method_names = {
            "INFO": ("info", "Info"),
            "WARN": ("warning", "warn", "Warning", "Warn"),
            "ERROR": ("error", "Error"),
            "DEBUG": ("debug", "Debug"),
        }.get(level_name, ())
        for method_name in method_names:
            func = getattr(self._host_logger, method_name, None)
            if callable(func):
                try:
                    func(msg, *args, **kwargs)
                    return
                except Exception:
                    continue

    def _call_py_logger(self, level_name, rendered_msg, kwargs):
        try:
            if level_name == "INFO":
                self._py_logger.info(rendered_msg, **kwargs)
            elif level_name == "WARN":
                self._py_logger.warning(rendered_msg, **kwargs)
            elif level_name == "ERROR":
                self._py_logger.error(rendered_msg, **kwargs)
            else:
                self._py_logger.debug(rendered_msg, **kwargs)
        except Exception:
            pass

    def _emit(self, level_name, msg, *args, **kwargs):
        rendered_msg = self._render(msg, args)
        self._call_host(level_name, msg, args, kwargs)
        self._call_py_logger(level_name, rendered_msg, kwargs)
        try:
            print(f"[{level_name}] {rendered_msg}", flush=True)
        except Exception:
            pass

    def info(self, msg, *args, **kwargs):
        self._emit("INFO", msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._emit("WARN", msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._emit("ERROR", msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._emit("DEBUG", msg, *args, **kwargs)


# 获取宿主环境logger（可能不存在或接口不完整），统一交给适配器处理
logger = _LoggerAdapter(globals().get("logger"))

from Agilebot import Arm, Extension, StatusCodeEnum
import copy
import functools
import math
import os
import platform
import socket
import sys
import tempfile
import threading
from datetime import datetime

# 全局Arm对象，用于长连接；_global_connect_fingerprint 记录上次成功 connect 的参数，变更则重连
# 指纹为 (控制柜 IP, 示教器 IP 或空串)，与官方 connect(arm_controller_ip, teach_panel_ip) 一致
_global_arm = None
_global_connect_fingerprint = None

# 明确指定导出的公开指令函数，隐藏私有辅助函数
__all__ = [
    'SetTF',
    'SetUF',
    'SetTF_R',
    'SetUF_R',
    'SetTF_PR',
    'SetUF_PR',
    'Incr',
    'Decr',
    'Strp',
    'TFShift',
    'DecToHex',
    'TurnCountToR',
    'RToTurnCount',
]


class PrecisionPose:
    """高精度位姿类，用于坐标变换计算"""
    def __init__(self, pose_list=None, x=0.0, y=0.0, z=0.0, w=0.0, p=0.0, r=0.0):
        if pose_list is not None:
            # 校验列表长度和类型
            if len(pose_list) != 6:
                raise ValueError("位姿列表必须包含6个元素：[X,Y,Z,W,P,R]")
            # 转换为浮点数，保证高精度
            self.X = float(pose_list[0])
            self.Y = float(pose_list[1])
            self.Z = float(pose_list[2])
            self.W = float(pose_list[3])
            self.P = float(pose_list[4])
            self.R = float(pose_list[5])
        else:
            # 兼容原有单独参数初始化
            self.X = float(x)
            self.Y = float(y)
            self.Z = float(z)
            self.W = float(w)
            self.P = float(p)
            self.R = float(r)

    def __str__(self):
        """完整高精度字符串输出（12位小数）"""
        return f"X={self.X:.12f}, Y={self.Y:.12f}, Z={self.Z:.12f}, W={self.W:.12f}, P={self.P:.12f}, R={self.R:.12f}"

    def to_compact_string(self):
        """精简字符串输出（6位小数）"""
        return f"{self.X:.6f} {self.Y:.6f} {self.Z:.6f} {self.W:.6f} {self.P:.6f} {self.R:.6f}"

    def to_list(self):
        """转换为位姿列表 [X,Y,Z,W,P,R]，便于对接机器人SDK"""
        return [self.X, self.Y, self.Z, self.W, self.P, self.R]


class PrecisionTransform:
    """高精度变换矩阵类，用于坐标变换计算"""
    def __init__(self):
        # 初始化4x4单位矩阵
        self.M = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]

    @classmethod
    def from_pose_zyx(cls, pose):
        """从Z-Y-X欧拉角创建变换矩阵（对应C#的SetFromPoseZYX）"""
        transform = cls()
        w_rad = math.radians(pose.W)
        p_rad = math.radians(pose.P)
        r_rad = math.radians(pose.R)

        cosR = math.cos(r_rad)
        sinR = math.sin(r_rad)
        cosP = math.cos(p_rad)
        sinP = math.sin(p_rad)
        cosW = math.cos(w_rad)
        sinW = math.sin(w_rad)

        # 核心：Z-Y-X旋转矩阵 Rz(R) * Ry(P) * Rx(W)（完全对齐C#的矩阵计算）
        transform.M[0][0] = cosR * cosP
        transform.M[0][1] = cosR * sinP * sinW - sinR * cosW
        transform.M[0][2] = cosR * sinP * cosW + sinR * sinW
        transform.M[0][3] = pose.X

        transform.M[1][0] = sinR * cosP
        transform.M[1][1] = sinR * sinP * sinW + cosR * cosW
        transform.M[1][2] = sinR * sinP * cosW - cosR * sinW
        transform.M[1][3] = pose.Y

        transform.M[2][0] = -sinP
        transform.M[2][1] = cosP * sinW
        transform.M[2][2] = cosP * cosW
        transform.M[2][3] = pose.Z

        transform.M[3][0] = 0.0
        transform.M[3][1] = 0.0
        transform.M[3][2] = 0.0
        transform.M[3][3] = 1.0
        return transform

    def get_pose_zyx(self):
        """从变换矩阵提取Z-Y-X欧拉角（对应C#的GetPoseZYX）"""
        pose = PrecisionPose()
        pose.X = self.M[0][3]
        pose.Y = self.M[1][3]
        pose.Z = self.M[2][3]

        # 提取欧拉角
        sy = math.sqrt(self.M[0][0] ** 2 + self.M[1][0] ** 2)
        singular = sy < 1e-12

        if not singular:
            pose.R = math.atan2(self.M[1][0], self.M[0][0])  # 绕Z轴
            pose.P = math.atan2(-self.M[2][0], sy)          # 绕Y轴
            pose.W = math.atan2(self.M[2][1], self.M[2][2])  # 绕X轴
        else:
            pose.R = math.atan2(-self.M[0][1], self.M[1][1])
            pose.P = math.atan2(-self.M[2][0], sy)
            pose.W = 0.0

        # 弧度转角度
        pose.W = math.degrees(pose.W)
        pose.P = math.degrees(pose.P)
        pose.R = math.degrees(pose.R)
        return pose

    def __mul__(self, other):
        """矩阵乘法"""
        result = PrecisionTransform()
        for i in range(4):
            for j in range(4):
                sum_val = 0.0
                for k in range(4):
                    sum_val += self.M[i][k] * other.M[k][j]
                result.M[i][j] = sum_val
        return result

    def inverse(self):
        """矩阵求逆"""
        inv = PrecisionTransform()

        # 旋转部分转置
        inv.M[0][0] = self.M[0][0]
        inv.M[0][1] = self.M[1][0]
        inv.M[0][2] = self.M[2][0]

        inv.M[1][0] = self.M[0][1]
        inv.M[1][1] = self.M[1][1]
        inv.M[1][2] = self.M[2][1]

        inv.M[2][0] = self.M[0][2]
        inv.M[2][1] = self.M[1][2]
        inv.M[2][2] = self.M[2][2]

        # 平移部分计算
        inv.M[0][3] = -(inv.M[0][0] * self.M[0][3] + inv.M[0][1] * self.M[1][3] + inv.M[0][2] * self.M[2][3])
        inv.M[1][3] = -(inv.M[1][0] * self.M[0][3] + inv.M[1][1] * self.M[1][3] + inv.M[1][2] * self.M[2][3])
        inv.M[2][3] = -(inv.M[2][0] * self.M[0][3] + inv.M[2][1] * self.M[1][3] + inv.M[2][2] * self.M[2][3])

        return inv


_CM_CONN_LOG_FILE_INITIALIZED = False
_CM_CONN_LOG_LOCK = threading.Lock()
_CM_CONN_LOG_RESOLVED_PATH = None

_LOG_BASENAME = "agilebot_cm_plugin.log"


def __cm_candidate_log_paths():
    """可写路径候选（优先环境变量，其次临时目录、工作目录、本文件目录、Unix 常见临时目录）。"""
    paths = []
    ev = os.environ.get("AGILEBOT_CM_LOG_FILE")
    if ev and str(ev).strip():
        paths.append(os.path.abspath(str(ev).strip()))
    try:
        paths.append(os.path.abspath(os.path.join(tempfile.gettempdir(), _LOG_BASENAME)))
    except Exception:
        pass
    try:
        paths.append(os.path.abspath(os.path.join(os.getcwd(), _LOG_BASENAME)))
    except Exception:
        pass
    try:
        here = globals().get("__file__")
        if here:
            paths.append(os.path.abspath(os.path.join(os.path.dirname(here), _LOG_BASENAME)))
    except Exception:
        pass
    if os.name != "nt":
        for extra in ("/tmp", "/var/tmp"):
            paths.append(os.path.join(extra, _LOG_BASENAME))
    seen = set()
    out = []
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def __cm_ensure_log_path():
    """解析首个可追加写入的日志路径并缓存。"""
    global _CM_CONN_LOG_RESOLVED_PATH
    if _CM_CONN_LOG_RESOLVED_PATH:
        try:
            with open(_CM_CONN_LOG_RESOLVED_PATH, "a", encoding="utf-8"):
                pass
            return _CM_CONN_LOG_RESOLVED_PATH
        except Exception:
            _CM_CONN_LOG_RESOLVED_PATH = None
    for p in __cm_candidate_log_paths():
        try:
            d = os.path.dirname(p)
            if d and not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        try:
            with open(p, "a", encoding="utf-8", newline="\n") as f:
                f.write("")
            _CM_CONN_LOG_RESOLVED_PATH = p
            return p
        except Exception:
            continue
    return None


def __cm_append_tagged_file(tag: str, msg: str):
    """向同一日志文件追加一行，tag 为 CM连接 / CM指令。"""
    global _CM_CONN_LOG_FILE_INITIALIZED
    path = __cm_ensure_log_path()
    if path is None:
        return
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [{tag}] {msg}\n"
    try:
        with _CM_CONN_LOG_LOCK:
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                if not _CM_CONN_LOG_FILE_INITIALIZED:
                    _CM_CONN_LOG_FILE_INITIALIZED = True
                    f.write(
                        f"\n======== CM 插件日志（连接 + 指令）========\n"
                        f"# 本文件路径: {path}\n"
                        f"# 自定义路径可设置环境变量 AGILEBOT_CM_LOG_FILE\n"
                    )
                f.write(line)
    except Exception:
        pass


def __cm_conn_log(msg: str):
    """连接排查：LoggerAdapter（logger+stdout）+ 日志文件。"""
    logger.info("[CM连接] %s", msg)
    __cm_append_tagged_file("CM连接", msg)


def __cm_instr_log(msg: str):
    """指令执行：与 [CM连接] 一并写入同一文件，便于界面/导出检索。"""
    logger.info("[CM指令] %s", msg)
    __cm_append_tagged_file("CM指令", msg)


def __cm_log_instruction(name: str):
    """装饰导出指令：须用 wraps 保留原签名，否则扩展服务会按 (*args,**kwargs) 要求 body 导致 400。"""

    def _wrap(fn):
        @functools.wraps(fn)
        def _inner(*args, **kwargs):
            try:
                parts = [repr(x) for x in args]
                parts.extend(f"{k}={v!r}" for k, v in kwargs.items())
                sig = ", ".join(parts)
                if len(sig) > 800:
                    sig = sig[:800] + "..."
                __cm_instr_log(f"{name} 开始({sig})")
            except Exception:
                __cm_instr_log(f"{name} 开始(参数摘要失败)")
            try:
                ret = fn(*args, **kwargs)
                if isinstance(ret, dict):
                    __cm_instr_log(
                        f"{name} 结束 success={ret.get('success')} "
                        f"error={ret.get('error')!r} message={ret.get('message')!r}"
                    )
                else:
                    __cm_instr_log(f"{name} 结束 返回类型={type(ret).__name__}")
                return ret
            except Exception as ex:
                __cm_instr_log(f"{name} 抛出异常: {ex!r}")
                raise

        return _inner

    return _wrap


def __cm_bootstrap_trace():
    """
    import 本模块时执行：证明 Python 已加载本文件。
    若仍完全没有磁盘日志且 stderr 也无输出，多为解释器/远程服务未加载本插件（与 INTERPRETER_SERVICE 相关）。
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"{ts} [CM引导] Python 已加载 CM.py (SDK2.0)。"
        f"后续连接步骤见 [CM连接] 前缀；本行不依赖是否执行自定义指令。\n"
    )
    ok = []
    for p in __cm_candidate_log_paths():
        try:
            d = os.path.dirname(p)
            if d and not os.path.isdir(d):
                os.makedirs(d, exist_ok=True)
        except Exception:
            pass
        try:
            with open(p, "a", encoding="utf-8", newline="\n") as f:
                f.write(line)
            ok.append(p)
        except Exception:
            continue
    try:
        sys.stderr.write(line)
        if ok:
            sys.stderr.write(f"[CM引导] 已写入以下可写路径: {ok}\n")
        else:
            sys.stderr.write(
                "[CM引导] 所有候选日志路径均不可写，请在示教器上设置环境变量 AGILEBOT_CM_LOG_FILE 指向 U 盘等可写路径。\n"
            )
        sys.stderr.flush()
    except Exception:
        pass


__cm_bootstrap_trace()


def __extension_try_teach_panel_ip(extension):
    """若 SDK 提供示教器地址 getter，则用于 connect 第二参数（环境变量未设置时）。"""
    for name in (
        "get_teach_panel_ip",
        "get_teach_pendant_ip",
        "get_teaching_panel_ip",
        "get_tp_ip",
    ):
        fn = getattr(extension, name, None)
        if not callable(fn):
            continue
        try:
            v = fn()
        except Exception as ex:
            __cm_conn_log("Extension.%s() 异常: %s" % (name, ex))
            continue
        if v is None:
            continue
        v = str(v).strip()
        if v:
            __cm_conn_log("示教器 IP 来自 Extension.%s(): %s" % (name, v))
            return v
    return None


def __detect_local_ipv4_towards(peer_ip: str):
    """
    通过 UDP 选路得到访问 peer 时本机所用 IPv4，用作示教器地址猜测。
    优先对控制柜 IP 选路（无公网时仍可用）；失败再尝试 8.8.8.8。
    设 AGILEBOT_DETECT_TEACH_IP=0/false/off 可关闭。
    """
    raw = os.environ.get("AGILEBOT_DETECT_TEACH_IP")
    if raw is not None and str(raw).strip().lower() in ("0", "false", "no", "off"):
        return None
    if not peer_ip:
        return None
    for target in (peer_ip, "8.8.8.8"):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.settimeout(0.8)
                s.connect((target, 7))
                ip = s.getsockname()[0]
            finally:
                s.close()
            if ip and not str(ip).startswith("127."):
                return str(ip).strip()
        except Exception:
            continue
    return None


def __resolve_robot_and_teach_ips():
    """
    解析 connect(控制柜, 示教器?) 所需地址。

    控制柜：AGILEBOT_ROBOT_IP / ROBOT_IP 优先，否则 Extension.get_robot_ip()。
    示教器：AGILEBOT_TEACH_PANEL_IP / TEACH_PANEL_IP 优先，否则尝试 Extension 上常见 getter。
    在 ARM（非 x86_64/amd64）且仍无示教器地址时，默认用本机检测 IPv4 作为第二参数
    （可设 AGILEBOT_AUTO_TEACH_IP_ON_ARM=0 关闭）。

    返回 (robot_ip 或 None, teach_panel_ip 或 None)；仅当至少一端需从 Extension 读取时才实例化 Extension。
    """
    robot_ip = None
    for env_key in ("AGILEBOT_ROBOT_IP", "ROBOT_IP"):
        override = os.environ.get(env_key)
        if override:
            override = str(override).strip()
            if override:
                __cm_conn_log("控制柜 IP 来自环境变量 %s: %s" % (env_key, override))
                robot_ip = override
                break

    teach_ip = None
    for env_key in ("AGILEBOT_TEACH_PANEL_IP", "TEACH_PANEL_IP"):
        v = os.environ.get(env_key)
        if v:
            v = str(v).strip()
            if v:
                __cm_conn_log("示教器 IP 来自环境变量 %s: %s" % (env_key, v))
                teach_ip = v
                break

    need_extension = robot_ip is None or teach_ip is None
    if not need_extension:
        return robot_ip, teach_ip

    try:
        extension = Extension()
        if robot_ip is None:
            raw = extension.get_robot_ip()
            if raw is not None:
                raw = str(raw).strip()
            if raw:
                __cm_conn_log("Extension.get_robot_ip() 返回控制柜 IP: %s" % raw)
                robot_ip = raw
            else:
                __cm_conn_log("Extension.get_robot_ip() 返回空字符串或 None")
        if teach_ip is None:
            teach_ip = __extension_try_teach_panel_ip(extension)
    except Exception as ex:
        logger.error("Extension 解析连接地址失败: %s", ex)
        __cm_conn_log("Extension 解析连接地址异常: %s" % ex)

    if (
        teach_ip is None
        and robot_ip
        and not __cm_default_local_proxy_when_unset()
    ):
        raw_auto = os.environ.get("AGILEBOT_AUTO_TEACH_IP_ON_ARM")
        if raw_auto is None or str(raw_auto).strip().lower() not in (
            "0",
            "false",
            "no",
            "off",
        ):
            guess = __detect_local_ipv4_towards(robot_ip)
            if guess and guess != robot_ip:
                __cm_conn_log(
                    "ARM 侧未取到示教器 IP：使用本机检测 IPv4 %s 作为 connect 第二参数"
                    % guess
                    + "（可用 AGILEBOT_TEACH_PANEL_IP 覆盖；AGILEBOT_AUTO_TEACH_IP_ON_ARM=0 关闭）"
                )
                teach_ip = guess

    return robot_ip, teach_ip


def __connect_fingerprint(controller_ip: str, teach_panel_ip):
    """与当前 connect 调用参数一致的身份，用于判断是否需要丢弃长连接。"""
    tp = teach_panel_ip if teach_panel_ip else ""
    return (controller_ip, tp)


def __cm_default_local_proxy_when_unset():
    """SDK 附带的本机代理为 linux_amd64；ARM 示教器上启用会 Exec format error。"""
    m = (platform.machine() or "").lower()
    return m in ("x86_64", "amd64")


def __create_arm_instance():
    """
    构造 Arm（见官方文档 Arm(local_proxy=...) 与 develop/Python_v2.0.0.0/example 用法）。

    环境变量 AGILEBOT_ARM_LOCAL_PROXY: true/1/yes/on 为 True；false/0/no/off 为 False。

    未设置时：x86_64/amd64 默认 True（等同 AGILEBOT_ARM_LOCAL_PROXY=true，便于 PC 扩展服务）；
    其余架构（如 aarch64 示教器）默认 False，避免执行 amd64 代理进程失败。
    """
    raw = os.environ.get("AGILEBOT_ARM_LOCAL_PROXY")
    mach = platform.machine() or "?"

    def _parse_env(s):
        t = str(s).strip().lower()
        if t in ("1", "true", "yes", "on"):
            return True
        if t in ("0", "false", "no", "off"):
            return False
        return None

    if raw is None:
        use = __cm_default_local_proxy_when_unset()
        __cm_conn_log(
            "未设置 AGILEBOT_ARM_LOCAL_PROXY；CPU=%s，默认 Arm(local_proxy=%s)"
            % (mach, use)
            + ("（x86_64/amd64 等同 true；ARM 请保持 False 或依赖内置代理）" if use else "（避免 linux_amd64 代理在 ARM 上 Exec format error）")
        )
        return Arm(local_proxy=use)

    parsed = _parse_env(raw)
    if parsed is not None:
        __cm_conn_log(
            "AGILEBOT_ARM_LOCAL_PROXY=%r，创建 Arm(local_proxy=%s)" % (raw, parsed)
        )
        return Arm(local_proxy=parsed)

    fallback = __cm_default_local_proxy_when_unset()
    __cm_conn_log(
        "AGILEBOT_ARM_LOCAL_PROXY 未识别(%r)；CPU=%s，回退 Arm(local_proxy=%s)"
        % (raw, mach, fallback)
    )
    return Arm(local_proxy=fallback)


def __arm_connect(arm, controller_ip: str, teach_panel_ip):
    """按官方签名连接；失败时由调用方 disconnect（参见文档 connect 示例）。"""
    if teach_panel_ip:
        __cm_conn_log(f"调用 connect(控制柜={controller_ip}, 示教器={teach_panel_ip})")
        return arm.connect(controller_ip, teach_panel_ip)
    __cm_conn_log(f"调用 connect(控制柜={controller_ip})")
    return arm.connect(controller_ip)


def __disconnect_global_arm():
    """释放全局 Arm 连接（官方推荐 disconnect()）。"""
    global _global_arm, _global_connect_fingerprint
    arm = _global_arm
    _global_arm = None
    _global_connect_fingerprint = None
    if arm is None:
        __cm_conn_log("disconnect_global_arm: 无活动连接，跳过")
        return
    used = None
    for name in ("disconnect", "Disconnect", "close", "Close"):
        fn = getattr(arm, name, None)
        if callable(fn):
            try:
                fn()
                used = name
                break
            except Exception as ex:
                logger.warning("[CM连接] %s() 异常: %s", name, ex)
    __cm_conn_log(f"全局 Arm 已释放，调用的断开方法: {used or '无可用方法'}")


def __arm_is_connected(arm):
    """
    查询 Arm 是否已连接。SDK 2.0.1.0 起标准方法为 is_connected()（原 is_connect 已更名）；
    仍兼容仅提供 is_connect 的旧包。
    """
    fn = getattr(arm, "is_connected", None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            pass
    fn = getattr(arm, "is_connect", None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            pass
    return False


def __get_arm_connection():
    """
    获取Arm连接（长连接机制）
    如果未连接则连接，已连接则复用；若控制柜/示教器连接参数变化则先 disconnect 再连。

    返回：
    - Arm: Arm对象，失败返回None
    - str: 错误信息，成功返回None
    """
    global _global_arm, _global_connect_fingerprint

    try:
        __cm_conn_log("开始获取 Arm 连接")
        robot_ip, teach_opt = __resolve_robot_and_teach_ips()
        if robot_ip is None:
            __cm_conn_log("失败: 无法解析控制柜 IP（检查 Extension / 环境变量 AGILEBOT_ROBOT_IP）")
            return None, "无法获取机器人IP地址"
        fp = __connect_fingerprint(robot_ip, teach_opt)
        __cm_conn_log(f"当前连接指纹 (控制柜,示教器): {fp}")

        if _global_arm is not None:
            if _global_connect_fingerprint is not None and fp != _global_connect_fingerprint:
                logger.warning(
                    f"检测到连接参数变化（已连接 {_global_connect_fingerprint} -> 当前 {fp}），断开旧连接后重连"
                )
                __cm_conn_log(f"指纹变化，丢弃旧连接: {_global_connect_fingerprint} -> {fp}")
                __disconnect_global_arm()
            else:
                try:
                    if __arm_is_connected(_global_arm):
                        if _global_connect_fingerprint is None:
                            _global_connect_fingerprint = fp
                        __cm_conn_log("复用已有连接，连接状态为已连接")
                        return _global_arm, None
                except Exception as ex:
                    __cm_conn_log(f"连接状态检查异常，将重连: {ex}")
                __cm_conn_log("已有 Arm 实例但未连接或状态异常，执行断开并重建")
                __disconnect_global_arm()

        _global_arm = __create_arm_instance()
        ret = __arm_connect(_global_arm, robot_ip, teach_opt)
        if ret != StatusCodeEnum.OK:
            __disconnect_global_arm()
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            __cm_conn_log(f"connect 失败: {error_msg} (返回值: {ret!r})")
            __cm_conn_log(
                "排查提示：确认示教器与控制柜同网段且可访问该 IP；若系统里控制柜地址已改，"
                "可设环境变量 AGILEBOT_ROBOT_IP 覆盖 Extension 返回值；ARM 下已自动补示范教器 IP 时仍失败，"
                "请用 AGILEBOT_TEACH_PANEL_IP 改为示教器真实 IP；也可设 AGILEBOT_AUTO_TEACH_IP_ON_ARM=0 后仅用单参数 connect。"
            )
            if not __cm_default_local_proxy_when_unset():
                __cm_conn_log(
                    "当前 CPU 非 x86_64/amd64：请勿设 AGILEBOT_ARM_LOCAL_PROXY=true（本机代理为 linux_amd64，"
                    "在示教器上会 Exec format error）；本条「无法连接控制器」与网络/双参数 connect 有关，与是否设 true 无关。"
                )
            return None, f"连接机器人失败，错误代码：{error_msg}"

        _global_connect_fingerprint = fp
        __cm_conn_log(f"connect 成功，指纹已记录: {fp}")
        return _global_arm, None

    except Exception as ex:
        logger.error(f"获取Arm连接失败: {ex}")
        __cm_conn_log(f"获取 Arm 连接未捕获异常: {ex}")
        __disconnect_global_arm()
        return None, f"获取连接失败：{str(ex)}"


def __get_param_name(param_index: int):
    """
    将参数编号转换为属性名（SDK 2.0.0.0中直接使用a/b/c，不再需要r/p/y转换）

    参数：
    - param_index: 1-6 (1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C)

    返回：
    - str: 属性名 ('x', 'y', 'z', 'a', 'b', 'c')
    """
    param_map = {
        1: 'x',  # X坐标
        2: 'y',  # Y坐标
        3: 'z',  # Z坐标
        4: 'a',  # 绕X轴旋转角度 (A)
        5: 'b',  # 绕Y轴旋转角度 (B)
        6: 'c'   # 绕Z轴旋转角度 (C)
    }
    return param_map.get(param_index)


def __create_r_register(arm, r_id: int, initial_value: float = 0.0):
    """
    创建并初始化R寄存器（如果不存在）

    参数：
    - arm: Arm对象
    - r_id: R寄存器编号
    - initial_value: 初始值，默认为0.0

    返回：
    - tuple: (StatusCodeEnum, 是否创建成功)
    """
    try:
        # 尝试读取R寄存器，如果存在则直接返回
        r_value, ret = arm.register.read_R(r_id)
        if ret == StatusCodeEnum.OK:
            logger.info(f"R寄存器[{r_id}]已存在，无需创建")
            return StatusCodeEnum.OK, False

        # R寄存器不存在，尝试通过写入来创建
        logger.info(f"R寄存器[{r_id}]不存在，尝试自动创建（初始值={initial_value}）...")

        # 尝试写入初始值来创建R寄存器
        ret = arm.register.write_R(r_id, initial_value)
        if ret == StatusCodeEnum.OK:
            logger.info(f"成功创建R寄存器[{r_id}]（初始值={initial_value}）")
            # 验证创建是否成功
            verify_value, verify_ret = arm.register.read_R(r_id)
            if verify_ret == StatusCodeEnum.OK:
                logger.info(f"R寄存器[{r_id}]创建并验证成功，当前值={verify_value}")
                return StatusCodeEnum.OK, True
            else:
                logger.warning(f"R寄存器[{r_id}]写入成功但验证失败，错误代码：{verify_ret}")
                return StatusCodeEnum.OK, True  # 仍然返回成功，因为write_R成功了
        else:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"创建R寄存器[{r_id}]失败，错误代码：{error_msg}")
            return ret, False

    except Exception as ex:
        logger.error(f"创建R寄存器[{r_id}]时发生异常：{ex}")
        return StatusCodeEnum.CONTROLLER_ERROR, False


def __create_pr_register(arm, pr_id: int):
    """
    创建并初始化PR寄存器（如果不存在）

    参数：
    - arm: Arm对象
    - pr_id: PR寄存器编号

    返回：
    - tuple: (pr_register对象, StatusCodeEnum) 或 (None, 错误代码)
    """
    try:
        # 尝试读取PR寄存器，如果存在则直接返回
        pr_register, ret = arm.register.read_PR(pr_id)
        if ret == StatusCodeEnum.OK:
            logger.info(f"PR寄存器[{pr_id}]已存在，无需创建")
            return pr_register, ret

        # PR寄存器不存在，需要创建
        logger.info(f"PR寄存器[{pr_id}]不存在，开始创建...")

        # 尝试通过写入一个初始化的PR寄存器对象来创建
        # 需要根据SDK的实际结构创建PR寄存器对象
        # 这里先尝试读取一个已存在的PR寄存器作为模板（如果可能）
        # 或者创建一个新的PR寄存器对象

        # 方法1：尝试读取任意已存在的PR寄存器作为模板
        # 从PR[1]开始尝试，如果不存在则尝试PR[2]、PR[3]等，最多尝试10个
        template_pr = None
        template_ret = None
        for template_id in range(1, 11):
            template_pr, template_ret = arm.register.read_PR(template_id)
            if template_ret == StatusCodeEnum.OK:
                logger.debug(f"使用PR[{template_id}]作为模板创建PR[{pr_id}]")
                break

        if template_ret == StatusCodeEnum.OK and template_pr is not None:
            # 使用模板创建新的PR寄存器
            # 复制模板结构，但将所有值设为0
            pr_register = copy.deepcopy(template_pr)

            # 初始化所有分量为0
            if hasattr(pr_register, 'poseRegisterData') and \
               hasattr(pr_register.poseRegisterData, 'cartData') and \
               hasattr(pr_register.poseRegisterData.cartData, 'position'):
                pr_position = pr_register.poseRegisterData.cartData.position
                pr_position.x = 0.0
                pr_position.y = 0.0
                pr_position.z = 0.0
                pr_position.a = 0.0
                pr_position.b = 0.0
                pr_position.c = 0.0

                # 设置PR寄存器索引
                if hasattr(pr_register, 'id'):
                    pr_register.id = pr_id
                elif hasattr(pr_register, 'registerIndex'):
                    pr_register.registerIndex = pr_id
                elif hasattr(pr_register, 'index'):
                    pr_register.index = pr_id

                # 尝试写入PR寄存器（如果SDK支持通过写入来创建）
                ret = arm.register.write_PR(pr_register)
                if ret == StatusCodeEnum.OK:
                    logger.info(f"成功创建PR寄存器[{pr_id}]（使用模板）")
                    # 验证创建是否成功
                    verify_pr, verify_ret = arm.register.read_PR(pr_id)
                    if verify_ret == StatusCodeEnum.OK:
                        logger.info(f"PR寄存器[{pr_id}]创建并验证成功")
                        return verify_pr, StatusCodeEnum.OK
                    else:
                        logger.warning(f"PR寄存器[{pr_id}]写入成功但验证失败，错误代码：{verify_ret}")
                        return pr_register, StatusCodeEnum.OK  # 仍然返回成功，因为write_PR成功了
                else:
                    error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
                    logger.error(f"写入PR寄存器[{pr_id}]失败，错误代码：{error_msg}")
                    return None, ret
            else:
                logger.error(f"PR寄存器模板结构不正确")
                return None, StatusCodeEnum.INVALID_PARAMETER
        else:
            # 方法2：如果没有任何PR寄存器存在，无法创建模板
            logger.error(f"无法创建PR寄存器[{pr_id}]：系统中没有任何PR寄存器可以作为模板")
            logger.error(f"请先在示教器中至少创建一个PR寄存器（如PR[1]），然后再使用此功能")
            return None, StatusCodeEnum.NOT_FOUND

    except Exception as ex:
        logger.error(f"创建PR寄存器[{pr_id}]时发生异常：{ex}")
        return None, StatusCodeEnum.CONTROLLER_ERROR


@__cm_log_instruction("SetTF")
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

    # 验证Value为数值类型
    try:
        Value = float(Value)
    except (ValueError, TypeError):
        return {"success": False, "error": f"无效的参数值：{Value}，必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 获取现有坐标系（SDK 2.0.0.0使用TF子类）
        coordinate, ret = arm.coordinate_system.TF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 更新参数值（保留三位小数）
        Value = round(float(Value), 3)

        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # 参数映射：1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C
        param_map = {1: 'x', 2: 'y', 3: 'z', 4: 'a', 5: 'b', 6: 'c'}
        data_attr = param_map.get(Pos)
        if data_attr is None:
            return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}

        setattr(coordinate.data, data_attr, Value)

        # 更新坐标系
        ret = arm.coordinate_system.TF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"TF坐标系[{ID}]的{param_display}参数已更新为{Value}"
        }

    except Exception as ex:
        logger.error(f"SetTF执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("SetUF")
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

    # 验证Value为数值类型
    try:
        Value = float(Value)
    except (ValueError, TypeError):
        return {"success": False, "error": f"无效的参数值：{Value}，必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 获取现有坐标系（SDK 2.0.0.0使用UF子类）
        coordinate, ret = arm.coordinate_system.UF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 更新参数值（保留三位小数）
        Value = round(float(Value), 3)

        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # 参数映射：1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C
        param_map = {1: 'x', 2: 'y', 3: 'z', 4: 'a', 5: 'b', 6: 'c'}
        data_attr = param_map.get(Pos)
        if data_attr is None:
            return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}

        setattr(coordinate.data, data_attr, Value)

        # 更新坐标系
        ret = arm.coordinate_system.UF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"UF坐标系[{ID}]的{param_display}参数已更新为{Value}"
        }

    except Exception as ex:
        logger.error(f"SetUF执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("SetTF_R")
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

    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取R寄存器
        r_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        # 获取现有坐标系（SDK 2.0.0.0使用TF子类）
        coordinate, ret = arm.coordinate_system.TF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 更新参数值（保留三位小数）
        Value = round(float(r_value), 3)

        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # 参数映射：1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C
        param_map = {1: 'x', 2: 'y', 3: 'z', 4: 'a', 5: 'b', 6: 'c'}
        data_attr = param_map.get(Pos)
        if data_attr is None:
            return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}

        setattr(coordinate.data, data_attr, Value)

        # 更新坐标系
        ret = arm.coordinate_system.TF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"TF坐标系[{ID}]的{param_display}参数已从R寄存器[{R_ID}]更新为{Value}"
        }

    except Exception as ex:
        logger.error(f"SetTF_R执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("SetUF_R")
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

    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取R寄存器
        r_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        # 获取现有坐标系（SDK 2.0.0.0使用UF子类）
        coordinate, ret = arm.coordinate_system.UF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 更新参数值（保留三位小数）
        Value = round(float(r_value), 3)

        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # 参数映射：1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C
        param_map = {1: 'x', 2: 'y', 3: 'z', 4: 'a', 5: 'b', 6: 'c'}
        data_attr = param_map.get(Pos)
        if data_attr is None:
            return {"success": False, "error": f"无效的位置参数：{Pos}，必须是1-6之一"}

        setattr(coordinate.data, data_attr, Value)

        # 更新坐标系
        ret = arm.coordinate_system.UF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        param_names = {1: 'X', 2: 'Y', 3: 'Z', 4: 'A', 5: 'B', 6: 'C'}
        param_display = param_names.get(Pos, f'参数{Pos}')
        return {
            "success": True,
            "message": f"UF坐标系[{ID}]的{param_display}参数已从R寄存器[{R_ID}]更新为{Value}"
        }

    except Exception as ex:
        logger.error(f"SetUF_R执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("SetTF_PR")
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
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取PR寄存器
        pr_register, ret = arm.register.read_PR(PR_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{error_msg}"}

        # 检查PR寄存器数据类型
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{PR_ID}]数据格式不正确，必须包含位姿数据"}

        # 获取现有坐标系（SDK 2.0.0.0使用TF子类）
        coordinate, ret = arm.coordinate_system.TF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
        # SDK 2.0.0.0中，坐标系数据直接使用a/b/c，不再需要r/p/y转换
        pr_position = pr_register.poseRegisterData.cartData.position
        # 更新坐标系数据（直接映射：x->x, y->y, z->z, a->a, b->b, c->c）
        coordinate.data.x = round(pr_position.x, 3)
        coordinate.data.y = round(pr_position.y, 3)
        coordinate.data.z = round(pr_position.z, 3)
        coordinate.data.a = round(pr_position.a, 3)
        coordinate.data.b = round(pr_position.b, 3)
        coordinate.data.c = round(pr_position.c, 3)

        # 更新坐标系
        ret = arm.coordinate_system.TF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        return {
            "success": True,
            "message": f"TF坐标系[{ID}]已从PR寄存器[{PR_ID}]更新：X={coordinate.data.x}, Y={coordinate.data.y}, Z={coordinate.data.z}, A={coordinate.data.a}, B={coordinate.data.b}, C={coordinate.data.c}"
        }

    except Exception as ex:
        logger.error(f"SetTF_PR执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("SetUF_PR")
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
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取PR寄存器
        pr_register, ret = arm.register.read_PR(PR_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{error_msg}"}

        # 检查PR寄存器数据类型
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{PR_ID}]数据格式不正确，必须包含位姿数据"}

        # 获取现有坐标系（SDK 2.0.0.0使用UF子类）
        coordinate, ret = arm.coordinate_system.UF.get(ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取坐标系失败，错误代码：{error_msg}"}

        # 从PR寄存器读取XYZABC值并更新到坐标系（保留三位小数）
        # SDK 2.0.0.0中，坐标系数据直接使用a/b/c，不再需要r/p/y转换
        pr_position = pr_register.poseRegisterData.cartData.position
        # 更新坐标系数据（直接映射：x->x, y->y, z->z, a->a, b->b, c->c）
        coordinate.data.x = round(pr_position.x, 3)
        coordinate.data.y = round(pr_position.y, 3)
        coordinate.data.z = round(pr_position.z, 3)
        coordinate.data.a = round(pr_position.a, 3)
        coordinate.data.b = round(pr_position.b, 3)
        coordinate.data.c = round(pr_position.c, 3)

        # 更新坐标系
        ret = arm.coordinate_system.UF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新坐标系失败，错误代码：{error_msg}"}

        return {
            "success": True,
            "message": f"UF坐标系[{ID}]已从PR寄存器[{PR_ID}]更新：X={coordinate.data.x}, Y={coordinate.data.y}, Z={coordinate.data.z}, A={coordinate.data.a}, B={coordinate.data.b}, C={coordinate.data.c}"
        }

    except Exception as ex:
        logger.error(f"SetUF_PR执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("Incr")
def Incr(R_ID: int, Step: float = 1.0) -> dict:
    """
    R寄存器自增

    参数：
    - R_ID (int): R寄存器编号
    - Step (float): 自增步长，默认为1.0

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    # 验证Step为数值类型并转换为浮点数
    try:
        Step = float(Step)
    except (ValueError, TypeError):
        return {"success": False, "error": f"自增步长必须是数值类型，当前值：{Step}"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取R寄存器当前值
        current_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        # 计算新值
        new_value = float(current_value) + float(Step)

        # 写入新值
        ret = arm.register.write_R(R_ID, new_value)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"写入R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        return {
            "success": True,
            "message": f"R寄存器[{R_ID}]已自增{Step}，当前值：{current_value} -> {new_value}"
        }

    except Exception as ex:
        logger.error(f"Incr执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("Decr")
def Decr(R_ID: int, Step: float = 1.0) -> dict:
    """
    R寄存器自减

    参数：
    - R_ID (int): R寄存器编号
    - Step (float): 自减步长，默认为1.0

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    # 验证Step为数值类型并转换为浮点数
    try:
        Step = float(Step)
    except (ValueError, TypeError):
        return {"success": False, "error": f"自减步长必须是数值类型，当前值：{Step}"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取R寄存器当前值
        current_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        # 计算新值（减去步长）
        new_value = float(current_value) - float(Step)

        # 写入新值
        ret = arm.register.write_R(R_ID, new_value)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"写入R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        return {
            "success": True,
            "message": f"R寄存器[{R_ID}]已自减{Step}，当前值：{current_value} -> {new_value}"
        }

    except Exception as ex:
        logger.error(f"Decr执行失败: {ex}")
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("Strp")
def Strp(SR_ID: int, R_ID_Status: int, PR_ID: int, R_ID_Error: int) -> dict:
    """
    拆解字符串数据到PR寄存器（视觉数据格式）

    数据格式说明：
    SR寄存器中的字符串格式：以分隔符分隔的数据（自动检测分隔符类型）
    支持的分隔符：逗号","、分号";"、空格" "、制表符"\t"、竖线"|"等
    示例（1组数据）：SR[1] = "1,100.5,200.3,45.0"
    示例（2组数据）：SR[1] = "1,100.5,200.3,45.0,150.0,250.0,90.0"

    数据格式规则：
    1. 第一个数据为物料检测状态位
       - "1" = 有物料，可以处理
       - "0" = 无物料，不处理
    2. 状态位后的数据必须是3的倍数（X,Y,C为一组）
       - 示例：3个数据（1组）、6个数据（2组）、9个数据（3组）等
    3. 每组数据按顺序映射为 (X, Y, C)

    数据映射到PR寄存器：
    每个PR寄存器存储6个分量（X, Y, Z, A, B, C）
    数据映射规则：
    - 第1组：X1 → PR[PR_ID].x, Y1 → PR[PR_ID].y, C1 → PR[PR_ID].c
    - 第2组：X2 → PR[PR_ID+1].x, Y2 → PR[PR_ID+1].y, C2 → PR[PR_ID+1].c
    - 以此类推...
    - Z, A, B 分量保留PR寄存器原有的值，不修改

    状态码说明：
    - R_ID_Status：物料检测状态（1=有物料，0=无物料）
    - R_ID_Error：错误状态码（0=正确，1=错误）
      - 状态位=0（无物料）→ R_ID_Status=0, R_ID_Error=1（错误）
      - 状态位=1且数据格式正确（3的倍数）→ R_ID_Status=1, R_ID_Error=0（正确）
      - 状态位=1但数据格式错误（不是3的倍数）→ R_ID_Status=1, R_ID_Error=1（格式错误）

    参数：
    - SR_ID (int): 字符串寄存器编号，包含视觉数据
                   格式：状态位,X,Y,C 或 状态位,X1,Y1,C1,X2,Y2,C2,...
                   示例："1,100.5,200.3,45.0"
    - R_ID_Status (int): R寄存器编号，用于输出物料检测状态（1=有物料，0=无物料）
    - PR_ID (int): PR寄存器起始编号，用于保存拆解后的数据
    - R_ID_Error (int): R寄存器编号，用于输出错误状态码（0=正确，1=错误）

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    try:
        SR_ID = int(SR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "SR寄存器编号必须是数值类型"}

    try:
        R_ID_Status = int(R_ID_Status)
    except (ValueError, TypeError):
        return {"success": False, "error": "R_ID_Status寄存器编号必须是数值类型"}

    try:
        PR_ID = int(PR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "PR寄存器编号必须是数值类型"}

    try:
        R_ID_Error = int(R_ID_Error)
    except (ValueError, TypeError):
        return {"success": False, "error": "R_ID_Error寄存器编号必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # ========== 步骤1：读取字符串寄存器 ==========
        # 读取SR寄存器内容，格式示例："1,100.5,200.3,300.1,45.2,60.8,90.0"
        logger.info(f"步骤1：读取SR寄存器[{SR_ID}]")
        str_value, ret = arm.register.read_SR(SR_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"读取SR寄存器[{SR_ID}]失败，错误代码：{error_msg}")
            return {"success": False, "error": f"读取SR寄存器[{SR_ID}]失败，错误代码：{error_msg}"}
        logger.info(f"SR寄存器[{SR_ID}]内容：{str_value}")

        # 检查字符串是否为空
        if not str_value or len(str_value.strip()) == 0:
            logger.error(f"SR寄存器[{SR_ID}]内容为空，无法拆解")
            # 确保R寄存器存在并写入状态码
            __create_r_register(arm, R_ID_Status, 0)
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Status, 0)
            arm.register.write_R(R_ID_Error, 1)
            return {"success": False, "error": f"SR寄存器[{SR_ID}]内容为空，无法拆解"}

        # ========== 步骤2：自动检测分隔符并拆解字符串 ==========
        # 自动检测常见分隔符：逗号、分号、竖线、制表符、空格等
        # 按检测到的分隔符分割字符串，去除每个部分的前后空格
        logger.info(f"步骤2：自动检测分隔符并拆解字符串")

        def detect_delimiter(text):
            """
            自动检测字符串中使用的分隔符
            返回检测到的分隔符
            """
            # 常见分隔符列表（按优先级排序）
            common_delimiters = [',', ';', '|', '\t', ' ']

            # 检测使用的分隔符：选择能产生最多有效部分（非空）的分隔符
            detected_delimiter = None
            max_valid_parts = 0

            for delimiter in common_delimiters:
                parts = [p.strip() for p in text.split(delimiter)]
                valid_parts = [p for p in parts if p]  # 过滤空字符串
                if len(valid_parts) > max_valid_parts:
                    max_valid_parts = len(valid_parts)
                    detected_delimiter = delimiter

            # 如果没检测到常见分隔符，尝试检测其他字符
            if detected_delimiter is None or max_valid_parts < 2:
                # 查找第一个非数字、非小数点、非负号、非空格的字符作为分隔符
                for i, char in enumerate(text):
                    if i > 0 and char not in '0123456789.- \t':
                        detected_delimiter = char
                        logger.info(f"检测到自定义分隔符：'{char}'")
                        break

            # 如果还是没检测到，默认使用逗号
            if detected_delimiter is None:
                detected_delimiter = ','
                logger.info(f"未检测到分隔符，使用默认分隔符：逗号")
            else:
                # 显示分隔符的可读名称
                delimiter_names = {
                    ',': '逗号',
                    ';': '分号',
                    '|': '竖线',
                    '\t': '制表符',
                    ' ': '空格'
                }
                delimiter_name = delimiter_names.get(detected_delimiter, f"'{detected_delimiter}'")
                logger.info(f"检测到分隔符：{delimiter_name} ('{detected_delimiter}')")

            return detected_delimiter

        # 检测分隔符
        detected_delimiter = detect_delimiter(str_value)

        # 按检测到的分隔符拆解字符串
        values = [v.strip() for v in str_value.split(detected_delimiter)]
        logger.debug(f"拆解后的值：{values}")

        # 过滤空值（防止有连续逗号或空字符串）
        values = [v for v in values if v]

        if len(values) == 0:
            logger.error(f"SR寄存器[{SR_ID}]中没有有效数据")
            # 确保R寄存器存在并写入状态码
            __create_r_register(arm, R_ID_Status, 0)
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Status, 0)
            arm.register.write_R(R_ID_Error, 1)
            return {"success": False, "error": f"SR寄存器[{SR_ID}]中没有有效数据"}

        # ========== 步骤3：提取状态位（第一个数据） ==========
        # 第一个值是物料检测状态位
        # 示例：values[0] = "1" → status_value = 1（有物料）
        logger.info(f"步骤3：提取物料检测状态位（第一个值：{values[0]}）")
        try:
            status_value = int(float(values[0]))
            logger.info(f"物料检测状态位值：{status_value} ({'有物料' if status_value == 1 else '无物料'})")
        except (ValueError, TypeError):
            logger.error(f"SR寄存器[{SR_ID}]第一个值'{values[0]}'无法转换为状态位")
            # 确保R寄存器存在并写入状态码
            __create_r_register(arm, R_ID_Status, 0)
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Status, 0)
            arm.register.write_R(R_ID_Error, 1)
            return {"success": False, "error": f"SR寄存器[{SR_ID}]第一个值'{values[0]}'无法转换为状态位"}

        # ========== 步骤4：检查状态位并设置R_ID_Status ==========
        # 将物料检测状态写入R_ID_Status寄存器
        logger.info(f"步骤4：写入物料检测状态到R_ID_Status寄存器[{R_ID_Status}]")
        __create_r_register(arm, R_ID_Status, status_value)
        ret = arm.register.write_R(R_ID_Status, status_value)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.warning(f"写入R_ID_Status寄存器[{R_ID_Status}]失败，错误代码：{error_msg}")

        # ========== 步骤5：检查状态位 ==========
        # 状态位为0表示无物料，不处理，设置R_ID_Error=1（错误）
        if status_value == 0:
            logger.warning(f"状态位为0，无物料，不进行拆解")
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Error, 1)
            return {
                "success": False,
                "error": f"SR寄存器[{SR_ID}]状态位为0，无物料，不进行拆解"
            }

        # ========== 步骤6：检查是否有数据 ==========
        # 状态位为1，需要处理后面的数据（从第二个值开始）
        if len(values) < 2:
            logger.error(f"SR寄存器[{SR_ID}]只有状态位，没有数据")
            # 确保R寄存器存在并写入状态码（格式错误）
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Error, 1)
            return {"success": False, "error": f"SR寄存器[{SR_ID}]只有状态位，没有数据"}

        # ========== 步骤7：提取数据部分并验证格式 ==========
        # 数据部分：状态位之后的所有数据
        # 示例：values = ["1", "100.5", "200.3", "45.0"]
        #      data_values = ["100.5", "200.3", "45.0"]
        logger.info(f"步骤7：提取数据部分（跳过状态位）")
        data_values = values[1:]
        logger.info(f"数据部分：{data_values}，共{len(data_values)}个数据")

        # ========== 步骤8：验证数据格式（必须是3的倍数） ==========
        # 数据个数必须是3的倍数（X,Y,C为一组）
        if len(data_values) % 3 != 0:
            logger.error(f"SR寄存器[{SR_ID}]数据格式错误：数据个数{len(data_values)}不是3的倍数")
            __create_r_register(arm, R_ID_Error, 1)
            arm.register.write_R(R_ID_Error, 1)
            return {
                "success": False,
                "error": f"SR寄存器[{SR_ID}]数据格式错误：数据个数{len(data_values)}不是3的倍数，必须是3的倍数（X,Y,C为一组）"
            }
        logger.info(f"数据格式验证通过：{len(data_values)}个数据，共{len(data_values) // 3}组")

        # ========== 步骤9：将字符串值转换为浮点数 ==========
        # 将数据字符串转换为浮点数
        # 示例：["100.5", "200.3", "45.0"] → [100.5, 200.3, 45.0]
        logger.info(f"步骤9：将字符串值转换为浮点数")
        float_values = []
        for i, val in enumerate(data_values):
            try:
                float_val = float(val)
                float_values.append(float_val)
                logger.debug(f"  数据{i+1}：'{val}' → {float_val}")
            except (ValueError, TypeError):
                logger.error(f"第{i+1}个数据'{val}'无法转换为数值")
                # 确保R寄存器存在并写入状态码（数据格式错误）
                __create_r_register(arm, R_ID_Error, 1)
                arm.register.write_R(R_ID_Error, 1)
                return {"success": False, "error": f"第{i+1}个数据'{val}'无法转换为数值"}
        logger.info(f"转换完成，共{len(float_values)}个浮点数：{float_values}")

        # ========== 步骤10：设置R_ID_Error=0（格式正确） ==========
        logger.info(f"步骤10：数据格式正确，设置R_ID_Error寄存器[{R_ID_Error}]=0")
        __create_r_register(arm, R_ID_Error, 0)
        arm.register.write_R(R_ID_Error, 0)

        # ========== 步骤11：计算需要多少个PR寄存器 ==========
        # 每组3个数据（X,Y,C）写入一个PR寄存器
        # 计算公式：数据数量 / 3
        num_pr_registers = len(float_values) // 3
        logger.info(f"步骤11：计算需要{num_pr_registers}个PR寄存器（{len(float_values)}个数据，{num_pr_registers}组）")

        # ========== 步骤12：将数据写入PR寄存器 ==========
        # 按组处理数据，每组3个数据（X,Y,C）写入一个PR寄存器
        # 数据映射关系：
        #   - 第1组：数据[0] → PR[PR_ID].x, 数据[1] → PR[PR_ID].y, 数据[2] → PR[PR_ID].c
        #   - 第2组：数据[3] → PR[PR_ID+1].x, 数据[4] → PR[PR_ID+1].y, 数据[5] → PR[PR_ID+1].c
        #   - Z, A, B 保留PR寄存器原有的值，不修改
        current_pr_id = PR_ID
        pr_count = 0

        # 循环处理所有需要的PR寄存器
        while pr_count < num_pr_registers:
            logger.info(f"步骤12：处理PR寄存器[{current_pr_id}]（第{pr_count + 1}个PR寄存器，第{pr_count + 1}组数据）")
            # 尝试读取当前PR寄存器
            pr_register, ret = arm.register.read_PR(current_pr_id)

            # 如果PR寄存器不存在，返回错误（需要手动创建）
            if ret != StatusCodeEnum.OK:
                error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
                logger.error(f"PR寄存器[{current_pr_id}]不存在（错误代码：{error_msg}）")
                __create_r_register(arm, R_ID_Error, 1)
                arm.register.write_R(R_ID_Error, 1)
                return {
                    "success": False,
                    "error": f"PR寄存器[{current_pr_id}]不存在，请手动创建PR寄存器后再使用"
                }

            # 检查PR寄存器数据类型
            if not hasattr(pr_register, 'poseRegisterData') or \
               not hasattr(pr_register.poseRegisterData, 'cartData') or \
               not hasattr(pr_register.poseRegisterData.cartData, 'position'):
                logger.error(f"PR寄存器[{current_pr_id}]数据格式不正确，必须包含位姿数据")
                __create_r_register(arm, R_ID_Error, 1)
                arm.register.write_R(R_ID_Error, 1)
                return {"success": False, "error": f"PR寄存器[{current_pr_id}]数据格式不正确，必须包含位姿数据"}

            # 更新当前PR寄存器的X、Y、C分量，保留Z、A、B的原有值
            pr_position = pr_register.poseRegisterData.cartData.position

            # 保存原有的Z、A、B值
            original_z = pr_position.z
            original_a = pr_position.a
            original_b = pr_position.b

            # 计算当前组的数据索引
            group_start_idx = pr_count * 3  # 每组3个数据
            x_value = round(float_values[group_start_idx], 3)      # X
            y_value = round(float_values[group_start_idx + 1], 3)  # Y
            c_value = round(float_values[group_start_idx + 2], 3)  # C

            # 只更新X、Y、C三个分量，Z、A、B保留原值
            pr_position.x = x_value
            pr_position.y = y_value
            pr_position.c = c_value
            # Z、A、B保持原值不变

            logger.info(f"  设置PR[{current_pr_id}]：X={x_value}, Y={y_value}, C={c_value}（Z={original_z}, A={original_a}, B={original_b}保持不变）")

            # 写回PR寄存器
            logger.info(f"准备写入PR寄存器[{current_pr_id}]")

            # 确保PR寄存器对象包含正确的索引信息（如果需要）
            if hasattr(pr_register, 'id'):
                pr_register.id = current_pr_id
            elif hasattr(pr_register, 'registerIndex'):
                pr_register.registerIndex = current_pr_id
            elif hasattr(pr_register, 'index'):
                pr_register.index = current_pr_id

            # 写入PR寄存器
            ret = arm.register.write_PR(pr_register)

            if ret != StatusCodeEnum.OK:
                error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
                logger.error(f"写入PR寄存器[{current_pr_id}]失败，错误代码：{error_msg}")
                __create_r_register(arm, R_ID_Error, 1)
                arm.register.write_R(R_ID_Error, 1)
                return {
                    "success": False,
                    "error": f"写入PR寄存器[{current_pr_id}]失败，错误代码：{error_msg}。请检查：1) PR寄存器是否存在 2) PR寄存器是否被锁定 3) 数据格式是否正确"
                }
            logger.info(f"成功写入PR寄存器[{current_pr_id}]")

            current_pr_id += 1
            pr_count += 1

        # 构建成功消息
        pr_list = []
        for i in range(num_pr_registers):
            pr_list.append(f"PR[{PR_ID + i}]")
        pr_str = ", ".join(pr_list)

        logger.info(f"✅ 所有数据已成功写入PR寄存器：{pr_str}")
        logger.info(f"成功拆解{len(float_values)}个数据（{num_pr_registers}组），共使用{num_pr_registers}个PR寄存器")
        return {
            "success": True,
            "message": f"成功拆解{len(float_values)}个数据（{num_pr_registers}组）到{pr_str}，R_ID_Status={status_value}（物料状态），R_ID_Error=0（正确）"
        }

    except Exception as ex:
        logger.error(f"Strp执行失败，发生异常: {ex}", exc_info=True)
        # 发生异常时，确保R寄存器存在并写入状态码
        try:
            arm, _ = __get_arm_connection()
            if arm:
                __create_r_register(arm, R_ID_Status, 0)
                __create_r_register(arm, R_ID_Error, 1)
                arm.register.write_R(R_ID_Status, 0)
                arm.register.write_R(R_ID_Error, 1)
        except:
            pass
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("TFShift")
def TFShift(InputTF_ID: int = 1, ResultTF_ID: int = 3, CamPose_ID: int = 60, RefVis_ID: int = 61, ActVis_ID: int = 62) -> dict:
    """
    工具坐标系补正（基于视觉反馈）

    该指令通过读取不同的视觉目标点偏差与基准视觉位置的偏差，来计算工具坐标系的相对偏差，
    从而将偏差输出在工具坐标系中。

    参数：
    - InputTF_ID (int): 基准标定坐标系编号（1-30），默认1
    - ResultTF_ID (int): 最终算法计算后写入的坐标系编号（1-30），默认3
    - CamPose_ID (int): 拍照点PR寄存器编号，默认60
    - RefVis_ID (int): 基准视觉模板数据PR寄存器编号，默认61（需要手动写入）
    - ActVis_ID (int): 视觉输出的实际坐标数据PR寄存器编号，默认62（需要手动写入）

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    try:
        InputTF_ID = int(InputTF_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "InputTF_ID必须是数值类型"}
    if InputTF_ID < 1 or InputTF_ID > 30:
        return {"success": False, "error": f"InputTF_ID必须在1-30之间，当前值：{InputTF_ID}"}

    try:
        ResultTF_ID = int(ResultTF_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ResultTF_ID必须是数值类型"}
    if ResultTF_ID < 1 or ResultTF_ID > 30:
        return {"success": False, "error": f"ResultTF_ID必须在1-30之间，当前值：{ResultTF_ID}"}

    try:
        CamPose_ID = int(CamPose_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "CamPose_ID必须是数值类型"}

    try:
        RefVis_ID = int(RefVis_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "RefVis_ID必须是数值类型"}

    try:
        ActVis_ID = int(ActVis_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "ActVis_ID必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取基准工具坐标系数据（SDK 2.0.0.0使用TF子类）
        logger.info(f"读取基准工具坐标系[{InputTF_ID}]")
        coordinate, ret = arm.coordinate_system.TF.get(InputTF_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取基准工具坐标系[{InputTF_ID}]失败，错误代码：{error_msg}"}
        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # 转换为W/P/R格式（W绕X轴，P绕Y轴，R绕Z轴，对应a/b/c）
        tool_data = [
            coordinate.data.x,
            coordinate.data.y,
            coordinate.data.z,
            coordinate.data.a,  # W (绕X轴) = a
            coordinate.data.b,  # P (绕Y轴) = b
            coordinate.data.c   # R (绕Z轴) = c
        ]
        ut1_ut0 = PrecisionPose(tool_data)

        # 读取拍照点位姿（UT1在UF1中的位姿）
        logger.info(f"读取拍照点PR寄存器[{CamPose_ID}]")
        pr_register, ret = arm.register.read_PR(CamPose_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取拍照点PR寄存器[{CamPose_ID}]失败，错误代码：{error_msg}"}
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{CamPose_ID}]数据格式不正确，必须包含位姿数据"}
        pr_position = pr_register.poseRegisterData.cartData.position
        pr_data = [
            pr_position.x,
            pr_position.y,
            pr_position.z,
            pr_position.a,  # W (绕X轴) = a
            pr_position.b,  # P (绕Y轴) = b
            pr_position.c   # R (绕Z轴) = c
        ]
        ut1_uf1_pr2 = PrecisionPose(pr_data)

        # 读取基准视觉模板数据（工件C1在视觉坐标系中的位姿）
        logger.info(f"读取基准视觉模板PR寄存器[{RefVis_ID}]")
        pr_register, ret = arm.register.read_PR(RefVis_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取基准视觉模板PR寄存器[{RefVis_ID}]失败，错误代码：{error_msg}"}
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{RefVis_ID}]数据格式不正确，必须包含位姿数据"}
        pr_position = pr_register.poseRegisterData.cartData.position
        pr_data = [
            pr_position.x,
            pr_position.y,
            pr_position.z,
            pr_position.a,  # W (绕X轴) = a
            pr_position.b,  # P (绕Y轴) = b
            pr_position.c   # R (绕Z轴) = c
        ]
        c1_uf1 = PrecisionPose(pr_data)

        # 读取实际视觉坐标数据（工件C2在视觉坐标系中的位姿）
        logger.info(f"读取实际视觉坐标PR寄存器[{ActVis_ID}]")
        pr_register, ret = arm.register.read_PR(ActVis_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取实际视觉坐标PR寄存器[{ActVis_ID}]失败，错误代码：{error_msg}"}
        if not hasattr(pr_register, 'poseRegisterData') or \
           not hasattr(pr_register.poseRegisterData, 'cartData') or \
           not hasattr(pr_register.poseRegisterData.cartData, 'position'):
            return {"success": False, "error": f"PR寄存器[{ActVis_ID}]数据格式不正确，必须包含位姿数据"}
        pr_position = pr_register.poseRegisterData.cartData.position
        pr_data = [
            pr_position.x,
            pr_position.y,
            pr_position.z,
            pr_position.a,  # W (绕X轴) = a
            pr_position.b,  # P (绕Y轴) = b
            pr_position.c   # R (绕Z轴) = c
        ]
        c2_uf1 = PrecisionPose(pr_data)

        # 构建变换矩阵
        T_UT0_UT1 = PrecisionTransform.from_pose_zyx(ut1_ut0)
        T_UF1_UT1_PR2 = PrecisionTransform.from_pose_zyx(ut1_uf1_pr2)
        T_UF1_C1 = PrecisionTransform.from_pose_zyx(c1_uf1)
        T_UF1_C2 = PrecisionTransform.from_pose_zyx(c2_uf1)

        # 计算工件在工具坐标系中的位姿
        T_UT1_C1 = T_UF1_UT1_PR2.inverse() * T_UF1_C1
        T_UT1_C2 = T_UF1_UT1_PR2.inverse() * T_UF1_C2

        poseC1_in_UT1 = T_UT1_C1.get_pose_zyx()
        poseC2_in_UT1 = T_UT1_C2.get_pose_zyx()

        # 计算新的工具坐标系TF2相对于TF0的位姿
        T_UT0_C2 = T_UT0_UT1 * T_UT1_C2
        T_UT0_UT2 = T_UT0_C2 * T_UT1_C1.inverse()
        poseUT2_relative_to_UT0 = T_UT0_UT2.get_pose_zyx()

        # 验证计算（可选）
        T_UF1_UT0 = T_UF1_UT1_PR2 * T_UT0_UT1.inverse()
        T_UF1_UT2 = T_UF1_UT0 * T_UT0_UT2
        T_UT2_C2_actual = T_UF1_UT2.inverse() * T_UF1_C2
        poseC2_in_UT2_actual = T_UT2_C2_actual.get_pose_zyx()

        errorX = abs(poseC1_in_UT1.X - poseC2_in_UT2_actual.X)
        errorY = abs(poseC1_in_UT1.Y - poseC2_in_UT2_actual.Y)
        errorR = abs(poseC1_in_UT1.R - poseC2_in_UT2_actual.R)
        logger.info(f"误差分析: ΔX={errorX:.12e}, ΔY={errorY:.12e}, ΔR={errorR:.12e}")

        # 构建结果位姿列表
        ut2_pose_list = [
            poseUT2_relative_to_UT0.X,
            poseUT2_relative_to_UT0.Y,
            poseUT2_relative_to_UT0.Z,
            poseUT2_relative_to_UT0.W,
            poseUT2_relative_to_UT0.P,
            poseUT2_relative_to_UT0.R
        ]

        # 写入结果工具坐标系（SDK 2.0.0.0使用TF子类）
        logger.info(f"写入计算结果到工具坐标系[{ResultTF_ID}]")
        coordinate, ret = arm.coordinate_system.TF.get(ResultTF_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"获取工具坐标系[{ResultTF_ID}]失败，错误代码：{error_msg}"}

        # SDK 2.0.0.0中，坐标系数据存储在data属性中，直接包含x/y/z/a/b/c
        # W/P/R转换为a/b/c（W绕X轴=a, P绕Y轴=b, R绕Z轴=c）
        coordinate.data.x = ut2_pose_list[0]
        coordinate.data.y = ut2_pose_list[1]
        coordinate.data.z = ut2_pose_list[2]
        coordinate.data.a = ut2_pose_list[3]  # W (绕X轴) -> a
        coordinate.data.b = ut2_pose_list[4]  # P (绕Y轴) -> b
        coordinate.data.c = ut2_pose_list[5]  # R (绕Z轴) -> c

        ret = arm.coordinate_system.TF.update(coordinate)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"更新工具坐标系[{ResultTF_ID}]失败，错误代码：{error_msg}"}

        return {
            "success": True,
            "message": f"工具坐标系补正完成，结果已写入TF[{ResultTF_ID}]：X={ut2_pose_list[0]:.6f}, Y={ut2_pose_list[1]:.6f}, Z={ut2_pose_list[2]:.6f}, A={ut2_pose_list[3]:.6f}, B={ut2_pose_list[4]:.6f}, C={ut2_pose_list[5]:.6f}"
        }

    except Exception as ex:
        logger.error(f"TFShift执行失败: {ex}", exc_info=True)
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("DecToHex")
def DecToHex(R_ID: int, SR_ID: int) -> dict:
    """
    从十进制转换为十六进制

    参数：
    - R_ID (int): R寄存器编号，包含需要转换的十进制数（支持整数和浮点数）
    - SR_ID (int): SR寄存器编号，用于保存转换后的十六进制字符串

    转换规则：
    1. 浮点数处理：截断（直接丢弃小数部分，不四舍五入）
    2. 数值范围：32位整数（-2147483648 到 2147483647）
    3. 负数处理：使用32位补码形式表示
    4. 输出格式：固定8位十六进制字符串（大写，不足8位前面补零）

    示例：
    - R[1] = 255 → SR[1] = "000000FF"
    - R[1] = 255.99 → SR[1] = "000000FF"（截断）
    - R[1] = -1 → SR[1] = "FFFFFFFF"
    - R[1] = -255 → SR[1] = "FFFFFF01"
    - R[1] = 0 → SR[1] = "00000000"

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    # 参数验证
    # 验证R_ID为数值类型并转换为整数
    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    # 验证SR_ID为数值类型并转换为整数
    try:
        SR_ID = int(SR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "SR寄存器编号必须是数值类型"}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # ========== 步骤1：读取R寄存器值 ==========
        logger.info(f"步骤1：读取R寄存器[{R_ID}]")
        r_value, ret = arm.register.read_R(R_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}")
            return {"success": False, "error": f"读取R寄存器[{R_ID}]失败，错误代码：{error_msg}"}
        logger.info(f"R寄存器[{R_ID}]原始值：{r_value}（类型：{type(r_value).__name__}）")

        # ========== 步骤2：转换为浮点数（统一处理） ==========
        try:
            float_value = float(r_value)
        except (ValueError, TypeError):
            logger.error(f"R寄存器[{R_ID}]的值'{r_value}'无法转换为数值")
            return {"success": False, "error": f"R寄存器[{R_ID}]的值'{r_value}'无法转换为数值"}

        # ========== 步骤3：截断为整数（丢弃小数部分） ==========
        logger.info(f"步骤3：截断浮点数{float_value}为整数")
        int_value = int(float_value)  # 直接截断，不四舍五入
        logger.info(f"截断后的整数值：{int_value}")

        # ========== 步骤4：验证32位整数范围 ==========
        logger.info(f"步骤4：验证32位整数范围")
        INT32_MIN = -2147483648
        INT32_MAX = 2147483647
        if int_value < INT32_MIN or int_value > INT32_MAX:
            logger.error(f"数值{int_value}超出32位整数范围（{INT32_MIN} 到 {INT32_MAX}）")
            return {
                "success": False,
                "error": f"数值{int_value}超出32位整数范围（{INT32_MIN} 到 {INT32_MAX}）"
            }
        logger.info(f"数值范围验证通过：{int_value}在32位范围内")

        # ========== 步骤5：转换为32位补码（处理负数） ==========
        logger.info(f"步骤5：转换为32位补码")
        # 使用位运算确保是32位无符号整数（负数自动转换为补码）
        uint32_value = int_value & 0xFFFFFFFF
        logger.info(f"32位补码值（无符号整数）：{uint32_value} (0x{uint32_value:08X})")

        # ========== 步骤6：格式化为8位大写十六进制字符串 ==========
        logger.info(f"步骤6：格式化为8位大写十六进制字符串")
        # format(value, '08X') 表示：8位，大写，不足8位前面补零
        hex_string = format(uint32_value, '08X')
        logger.info(f"十六进制字符串：'{hex_string}'")

        # ========== 步骤7：写入SR寄存器 ==========
        logger.info(f"步骤7：写入SR寄存器[{SR_ID}]")
        ret = arm.register.write_SR(SR_ID, hex_string)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"写入SR寄存器[{SR_ID}]失败，错误代码：{error_msg}")
            return {"success": False, "error": f"写入SR寄存器[{SR_ID}]失败，错误代码：{error_msg}"}
        logger.info(f"成功写入SR寄存器[{SR_ID}]：'{hex_string}'")

        # ========== 步骤8：返回成功信息 ==========
        # 构建消息：显示原始值、截断后的整数值和十六进制结果
        original_display = f"{r_value}" if isinstance(r_value, int) or r_value == int_value else f"{r_value}（截断为{int_value}）"
        return {
            "success": True,
            "message": f"R寄存器[{R_ID}]的值{original_display}已转换为十六进制'{hex_string}'并写入SR寄存器[{SR_ID}]"
        }

    except Exception as ex:
        logger.error(f"DecToHex执行失败: {ex}", exc_info=True)
        return {"success": False, "error": f"执行失败：{str(ex)}"}


@__cm_log_instruction("TurnCountToR")
def TurnCountToR(PR_ID: int, R_ID: int, Joint_ID: int = 1) -> dict:
    """
    读取指定PR寄存器中的回转数（turnCircle）指定轴，并写入单个R寄存器

    参数：
    - PR_ID (int): PR寄存器编号（如 PR1 则传 1）
    - R_ID (int): R寄存器编号（单个R）
    - Joint_ID (int): 写入哪个关节轴（1=J1, 2=J2, ..., 6=J6），默认1

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    logger.info(f"TurnCountToR开始执行: PR_ID={PR_ID}, R_ID={R_ID}, Joint_ID={Joint_ID}")
    # 参数验证
    try:
        PR_ID = int(PR_ID)
    except (ValueError, TypeError):
        error_msg = "PR寄存器编号必须是数值类型"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        error_msg = "R寄存器编号必须是数值类型"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    try:
        Joint_ID = int(Joint_ID)
    except (ValueError, TypeError):
        error_msg = "Joint_ID必须是数值类型（1=J1, ..., 6=J6）"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    if Joint_ID < 1:
        error_msg = f"Joint_ID必须>=1，当前值：{Joint_ID}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        logger.error(f"获取Arm连接失败: {error}")
        return {"success": False, "error": error}

    try:
        logger.info(f"步骤1：读取PR寄存器[{PR_ID}]")
        pr_register, ret = arm.register.read_PR(PR_ID)
        logger.info(f"read_PR返回状态: {ret}")
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"读取PR寄存器[{PR_ID}]失败，错误代码：{error_msg}")
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{error_msg}"}

        # 兼容不同SDK结构：posture 可能在 poseRegisterData.posture 或 poseRegisterData.cartData.posture
        posture_obj = None
        pr_data = None
        if hasattr(pr_register, 'poseRegisterData'):
            pr_data = pr_register.poseRegisterData
            if hasattr(pr_data, 'posture') and pr_data.posture is not None:
                posture_obj = pr_data.posture
            elif hasattr(pr_data, 'cartData') and hasattr(pr_data.cartData, 'posture') and pr_data.cartData.posture is not None:
                posture_obj = pr_data.cartData.posture

        if posture_obj is None:
            logger.error(f"PR[{PR_ID}]未找到posture对象，pr_register类型={type(pr_register).__name__}")
            return {"success": False, "error": f"PR寄存器[{PR_ID}]中未找到姿态(posture)数据"}

        # 兼容字段命名：turnCircle / turn_circle
        turn_circle_values = None
        if hasattr(posture_obj, 'turnCircle'):
            turn_circle_values = posture_obj.turnCircle
        elif hasattr(posture_obj, 'turn_circle'):
            turn_circle_values = posture_obj.turn_circle

        # SDK字段兜底探测：扫描 posture/pr_data/cartData/pr_register 中带 turn 的列表字段
        if turn_circle_values is None:
            probe_sources = [("posture", posture_obj)]
            if pr_data is not None:
                probe_sources.append(("poseRegisterData", pr_data))
                if hasattr(pr_data, 'cartData'):
                    probe_sources.append(("cartData", pr_data.cartData))
            probe_sources.append(("pr_register", pr_register))

            for src_name, src_obj in probe_sources:
                try:
                    attr_names = [n for n in dir(src_obj) if not n.startswith('_')]
                except Exception:
                    continue
                for attr_name in attr_names:
                    low_name = attr_name.lower()
                    if "turn" not in low_name:
                        continue
                    try:
                        candidate = getattr(src_obj, attr_name)
                    except Exception:
                        continue
                    if isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                        turn_circle_values = candidate
                        logger.info(f"自动探测到回转数字段: {src_name}.{attr_name}")
                        break
                if turn_circle_values is not None:
                    break

        if turn_circle_values is None:
            try:
                posture_fields = [n for n in dir(posture_obj) if not n.startswith('_')]
            except Exception:
                posture_fields = []
            logger.error(f"PR[{PR_ID}]的posture缺少turn相关字段，posture类型={type(posture_obj).__name__}，可用字段={posture_fields}")
            return {"success": False, "error": f"PR寄存器[{PR_ID}]中未找到回转数(turnCircle/turn_circle)数据"}

        turn_circle = list(turn_circle_values)
        if len(turn_circle) == 0:
            logger.error(f"PR寄存器[{PR_ID}]的turnCircle为空")
            return {"success": False, "error": f"PR寄存器[{PR_ID}]的turnCircle为空，无法写入R寄存器"}

        joint_index = Joint_ID - 1
        if joint_index >= len(turn_circle):
            return {
                "success": False,
                "error": f"Joint_ID={Joint_ID}超出turnCircle长度（len={len(turn_circle)}）"
            }

        # 只写一个轴：J{JointStart} -> R[{Start_R_ID}]
        raw_value = turn_circle[joint_index]
        try:
            float_value = float(raw_value)
        except (ValueError, TypeError):
            logger.error(f"turnCircle[J{Joint_ID}]不是有效数值: {raw_value}")
            return {
                "success": False,
                "error": f"PR寄存器[{PR_ID}]的turnCircle[J{Joint_ID}]值'{raw_value}'不是有效数值，仅允许-1/0/1"
            }
        if not float_value.is_integer():
            logger.error(f"turnCircle[J{Joint_ID}]不是整数: {raw_value}")
            return {
                "success": False,
                "error": f"PR寄存器[{PR_ID}]的turnCircle[J{Joint_ID}]值为{raw_value}，必须是整数且仅允许-1/0/1"
            }
        value = int(float_value)
        if value not in (-1, 0, 1):
            logger.error(f"turnCircle[J{Joint_ID}]超出允许范围: {value}")
            return {
                "success": False,
                "error": f"PR寄存器[{PR_ID}]的turnCircle[J{Joint_ID}]值为{value}，仅允许-1/0/1"
            }

        logger.info(f"步骤2：写入回转数到R寄存器：J{Joint_ID}({raw_value}) -> R[{R_ID}]={value}")
        ret = arm.register.write_R(R_ID, value)
        logger.info(f"write_R返回状态: R[{R_ID}] -> {ret}")
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            logger.error(f"写入R寄存器[{R_ID}]失败，错误代码：{error_msg}")
            return {"success": False, "error": f"写入R寄存器[{R_ID}]失败，错误代码：{error_msg}"}

        logger.info(f"TurnCountToR执行成功: PR[{PR_ID}] J{Joint_ID} -> R[{R_ID}]={value}")
        return {
            "success": True,
            "message": f"已将PR[{PR_ID}]的J{Joint_ID}回转数（{raw_value}）写入R[{R_ID}]={value}"
        }

    except Exception as ex:
        logger.error(f"TurnCountToR执行失败: {ex}", exc_info=True)
        return {"success": False, "error": f"执行失败：{str(ex)}"}




@__cm_log_instruction("RToTurnCount")
def RToTurnCount(PR_ID: int, R_ID: int, Joint_ID: int = 1) -> dict:
    """
    将连续R寄存器中的值回写到PR寄存器的回转数（turnCircle）

    参数：
    - PR_ID (int): PR寄存器编号，写入其姿态中的turnCircle
    - R_ID (int): R寄存器编号（单个R）
    - Joint_ID (int): 需要回写的关节轴（1=J1, 2=J2, ..., 6=J6），默认1

    说明：
    - 不会清空整个 turnCircle
    - 只替换目标关节范围对应的值，其它关节保持不变

    返回：
    - dict: {"success": bool, "message": str, "error": str}
    """
    logger.info(
        f"RToTurnCount开始执行: PR_ID={PR_ID}, R_ID={R_ID}, Joint_ID={Joint_ID}"
    )
    # 参数验证
    try:
        PR_ID = int(PR_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "PR寄存器编号必须是数值类型"}

    try:
        R_ID = int(R_ID)
    except (ValueError, TypeError):
        return {"success": False, "error": "R寄存器编号必须是数值类型"}

    try:
        Joint_ID = int(Joint_ID)
    except (ValueError, TypeError):
        error_msg = "Joint_ID必须是数值类型（1=J1, ..., 6=J6）"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    if Joint_ID < 1:
        error_msg = f"Joint_ID必须>=1，当前值：{Joint_ID}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

    # 获取Arm连接（长连接机制）
    arm, error = __get_arm_connection()
    if arm is None:
        return {"success": False, "error": error}

    try:
        # 读取PR寄存器
        logger.info(f"步骤1：读取PR寄存器[{PR_ID}]")
        pr_register, ret = arm.register.read_PR(PR_ID)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取PR寄存器[{PR_ID}]失败，错误代码：{error_msg}"}

        # 兼容不同SDK结构：posture 可能在 poseRegisterData.posture 或 poseRegisterData.cartData.posture
        posture_obj = None
        pr_data = None
        if hasattr(pr_register, 'poseRegisterData'):
            pr_data = pr_register.poseRegisterData
            if hasattr(pr_data, 'posture') and pr_data.posture is not None:
                posture_obj = pr_data.posture
            elif hasattr(pr_data, 'cartData') and hasattr(pr_data.cartData, 'posture') and pr_data.cartData.posture is not None:
                posture_obj = pr_data.cartData.posture

        if posture_obj is None:
            logger.error(f"PR[{PR_ID}]中未找到可写入posture，pr_register类型={type(pr_register).__name__}")
            return {"success": False, "error": f"PR寄存器[{PR_ID}]中未找到可写入的姿态(posture)结构"}

        # 兼容字段命名：turnCircle / turn_circle / turn_cycle
        turn_circle_attr = None
        turn_circle_owner = posture_obj
        if hasattr(posture_obj, 'turnCircle'):
            turn_circle_attr = 'turnCircle'
        elif hasattr(posture_obj, 'turn_circle'):
            turn_circle_attr = 'turn_circle'
        elif hasattr(posture_obj, 'turn_cycle'):
            turn_circle_attr = 'turn_cycle'

        # SDK字段兜底探测：扫描 posture/pr_data/cartData/pr_register 中带 turn 的序列字段
        if turn_circle_attr is None:
            probe_sources = [("posture", posture_obj)]
            if pr_data is not None:
                probe_sources.append(("poseRegisterData", pr_data))
                if hasattr(pr_data, 'cartData'):
                    probe_sources.append(("cartData", pr_data.cartData))
            probe_sources.append(("pr_register", pr_register))

            for src_name, src_obj in probe_sources:
                try:
                    attr_names = [n for n in dir(src_obj) if not n.startswith('_')]
                except Exception:
                    continue
                for attr_name in attr_names:
                    if "turn" not in attr_name.lower():
                        continue
                    try:
                        candidate = getattr(src_obj, attr_name)
                    except Exception:
                        continue
                    if hasattr(candidate, "append") and hasattr(candidate, "pop"):
                        turn_circle_attr = attr_name
                        turn_circle_owner = src_obj
                        logger.info(f"自动探测到可写回转数字段: {src_name}.{attr_name}")
                        break
                    if isinstance(candidate, (list, tuple)):
                        turn_circle_attr = attr_name
                        turn_circle_owner = src_obj
                        logger.info(f"自动探测到回转数字段: {src_name}.{attr_name}")
                        break
                if turn_circle_attr is not None:
                    break

        if turn_circle_attr is None:
            try:
                posture_fields = [n for n in dir(posture_obj) if not n.startswith('_')]
            except Exception:
                posture_fields = []
            logger.error(f"PR[{PR_ID}]未找到可写turn字段，posture类型={type(posture_obj).__name__}，可用字段={posture_fields}")
            return {"success": False, "error": f"PR寄存器[{PR_ID}]中未找到可写入的回转数(turnCircle/turn_circle)结构"}

        # 获取现有turnCircle，并按关节下标写入（不清空，不组装重建）
        turn_circle_container = getattr(turn_circle_owner, turn_circle_attr)
        existing_turn_circle = list(turn_circle_container)
        if len(existing_turn_circle) == 0:
            return {"success": False, "error": f"PR寄存器[{PR_ID}]的turnCircle为空，无法回写"}

        joint_start_index = Joint_ID - 1
        if joint_start_index < 0 or joint_start_index >= len(existing_turn_circle):
            return {
                "success": False,
                "error": f"Joint_ID={Joint_ID}超出turnCircle长度（len={len(existing_turn_circle)}）"
            }

        # 只替换一个轴：turnCircle[joint_start_index]（即 J{Joint_ID}）
        target_index = joint_start_index
        old_value = existing_turn_circle[target_index]

        logger.info(
            f"步骤2：读取R[{R_ID}]并替换J{Joint_ID}回转数（turnCircle[{target_index}]）"
        )
        r_id = R_ID
        r_value, ret = arm.register.read_R(r_id)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"读取R寄存器[{r_id}]失败，错误代码：{error_msg}"}

        try:
            float_value = float(r_value)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": f"R寄存器[{r_id}]的值'{r_value}'不是有效数值，仅允许-1/0/1"
            }
        if not float_value.is_integer():
            return {
                "success": False,
                "error": f"R寄存器[{r_id}]的值为{r_value}，必须是整数且仅允许-1/0/1"
            }
        value = int(float_value)
        if value not in (-1, 0, 1):
            return {
                "success": False,
                "error": f"R寄存器[{r_id}]的值为{value}，仅允许-1/0/1"
            }

        logger.info(f"  替换：J{Joint_ID} 回转数 {old_value} -> {value}（来自R[{r_id}]）")
        existing_turn_circle[target_index] = value

        # 尽量原地写回（只替换一个index）
        logger.info(f"步骤3：写回PR[{PR_ID}]的J{Joint_ID}回转数")
        try:
            turn_circle_container[target_index] = int(existing_turn_circle[target_index])
        except Exception:
            setattr(turn_circle_owner, turn_circle_attr, [int(v) for v in existing_turn_circle])

        # 写回PR寄存器
        ret = arm.register.write_PR(pr_register)
        if ret != StatusCodeEnum.OK:
            error_msg = ret.errmsg if hasattr(ret, 'errmsg') else str(ret)
            return {"success": False, "error": f"写入PR寄存器[{PR_ID}]失败，错误代码：{error_msg}"}

        logger.info(f"RToTurnCount执行成功: PR[{PR_ID}] J{Joint_ID} 已替换 {old_value} -> {value}")
        return {
            "success": True,
            "message": f"已将R[{R_ID}]的值写入PR[{PR_ID}]的J{Joint_ID}回转数：{old_value} -> {value}"
        }

    except Exception as ex:
        logger.error(f"RToTurnCount执行失败: {ex}", exc_info=True)
        return {"success": False, "error": f"执行失败：{str(ex)}"}


