#!python
# -*- coding: utf-8 -*-
"""
插件打包脚本
将插件文件打包成tar.gz格式（.gbtapp），可直接导入到机器人系统中
"""

import os
import tarfile
import json
from datetime import datetime

def pack_plugin():
    """
    打包插件为.gbtapp文件（使用tar.gz格式）
    """
    
    # 插件目录
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_name = "CM"
    
    # 读取config.json获取版本信息
    config_path = os.path.join(plugin_dir, "config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    version = config.get('version', '0.1')
    
    # 生成插件包文件名（.gbtapp格式）
    plugin_filename = f"{plugin_name}_v{version}_{datetime.now().strftime('%Y%m%d')}.gbtapp"
    plugin_path = os.path.join(plugin_dir, plugin_filename)
    
    # 如果文件已存在，先删除
    if os.path.exists(plugin_path):
        os.remove(plugin_path)
        print(f"已删除旧文件: {plugin_filename}")
    
    # 需要打包的文件（Python文件名必须与插件名相同）
    files_to_pack = [
        "config.json",
        "CM.py"
    ]
    
    # 创建.gbtapp文件（使用tar.gz格式）
    # 使用gzip压缩，这是机器人系统期望的格式
    # 设置format='gnu'确保兼容性
    with tarfile.open(plugin_path, 'w:gz', format=tarfile.GNU_FORMAT) as tar:
        for file_name in files_to_pack:
            file_path = os.path.join(plugin_dir, file_name)
            if os.path.exists(file_path):
                # 添加文件到tar，确保文件在根目录
                tar.add(file_path, arcname=file_name)
                print(f"已添加: {file_name}")
            else:
                print(f"警告: 文件不存在 {file_name}")
    
    print(f"\n插件打包完成！")
    print(f"文件位置: {plugin_path}")
    print(f"文件大小: {os.path.getsize(plugin_path) / 1024:.2f} KB")
    print(f"文件格式: tar.gz (gzip压缩)")
    print(f"\n包含文件:")
    for file_name in files_to_pack:
        file_path = os.path.join(plugin_dir, file_name)
        if os.path.exists(file_path):
            print(f"  - {file_name}")
    print(f"\n可以将此 .gbtapp 文件导入到机器人系统中。")
    
    return plugin_path

if __name__ == "__main__":
    pack_plugin()

