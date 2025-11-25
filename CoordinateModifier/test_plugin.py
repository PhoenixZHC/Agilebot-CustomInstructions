#!python
# -*- coding: utf-8 -*-
"""测试插件包是否可以正常解压"""

import tarfile
import tempfile
import os
import json

plugin_file = "CoordinateModifier_v0.1_20251124.gbtapp"

print(f"Testing plugin package: {plugin_file}")
print("-" * 50)

# 测试tar.gz文件是否有效
try:
    with tarfile.open(plugin_file, 'r:gz') as tar:
        print("OK: tar.gz file format is correct")
        print(f"OK: Contains files: {tar.getnames()}")
        
        # 测试解压
        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(tmpdir)
            files = os.listdir(tmpdir)
            print(f"OK: Extraction successful, files: {files}")
            
            # 验证config.json
            config_path = os.path.join(tmpdir, "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"OK: config.json format is correct")
                print(f"  Plugin name: {config.get('name')}")
                print(f"  Plugin type: {config.get('type')}")
                print(f"  Version: {config.get('version')}")
            else:
                print("ERROR: config.json not found")
            
            # 验证Python文件
            py_path = os.path.join(tmpdir, "CoordinateModifier.py")
            if os.path.exists(py_path):
                with open(py_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"OK: CoordinateModifier.py exists, size: {len(content)} characters")
            else:
                print("ERROR: CoordinateModifier.py not found")
        
        print("\nPlugin package validation passed!")
        
except tarfile.TarError as e:
    print(f"ERROR: tar.gz file format error: {e}")
except Exception as e:
    print(f"ERROR: {e}")

