#!python
# -*- coding: utf-8 -*-
"""
插件打包脚本
将插件文件打包成 .gbtapp 文件（tar.gz格式）
"""

import os
import tarfile
import datetime
import json

def pack_plugin():
    """打包插件文件"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 插件文件列表
    plugin_files = ['config.json', 'CM.py']
    
    # 检查文件是否存在
    missing_files = []
    for file in plugin_files:
        file_path = os.path.join(script_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"错误：以下文件不存在：{', '.join(missing_files)}")
        return
    
    # 读取版本号
    config_path = os.path.join(script_dir, 'config.json')
    version = "0.1"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            version = config.get('version', '0.1')
    except:
        pass
    
    # 生成文件名：CM_v{version}_{YYYYMMDD}.gbtapp
    today = datetime.datetime.now().strftime('%Y%m%d')
    output_filename = f'CM_v{version}_{today}.gbtapp'
    output_path = os.path.join(script_dir, output_filename)
    
    # 删除旧文件（如果存在）
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"已删除旧文件: {output_filename}")
    
    # 创建tar.gz文件
    print(f"打包中: {output_filename}")
    with tarfile.open(output_path, 'w:gz') as tar:
        for file in plugin_files:
            file_path = os.path.join(script_dir, file)
            tar.add(file_path, arcname=file)
            print(f"已添加: {file}")
    
    # 获取文件大小
    file_size = os.path.getsize(output_path)
    file_size_kb = file_size / 1024
    
    print(f"\n打包完成！")
    print(f"文件位置: {output_path}")
    print(f"文件大小: {file_size_kb:.2f} KB")
    print(f"文件格式: tar.gz (gzip压缩)")
    print(f"\n包含文件:")
    for file in plugin_files:
        print(f"  - {file}")
    print(f"\n可以将 .gbtapp 文件导入到机器人系统中。")

if __name__ == '__main__':
    pack_plugin()




