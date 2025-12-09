#!python
# -*- coding: utf-8 -*-
"""
测试SDK导入
"""

try:
    from Agilebot.IR.A.arm import Arm
    from Agilebot.IR.A.extension import Extension
    from Agilebot.IR.A.status_code import StatusCodeEnum
    from Agilebot.IR.A.sdk_types import CoordinateSystemType
    print("All SDK modules imported successfully!")
    print(f"  - Arm: {Arm}")
    print(f"  - Extension: {Extension}")
    print(f"  - StatusCodeEnum: {StatusCodeEnum}")
    print(f"  - CoordinateSystemType: {CoordinateSystemType}")
except ImportError as e:
    print(f"SDK import failed: {e}")
    import sys
    print(f"Python路径: {sys.path}")

