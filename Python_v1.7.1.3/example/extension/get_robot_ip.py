#!python
from Agilebot.IR.A.extension import Extension

# 初始化插件
extension = Extension()

# 获取IP
res = extension.get_robot_ip()
assert robot_ip == None
