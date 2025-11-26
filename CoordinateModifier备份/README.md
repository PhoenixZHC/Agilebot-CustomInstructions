# 坐标系修改插件 (CoordinateModifier)

## 功能说明

本插件提供三个函数用于修改机器人的用户坐标系和工具坐标系：

1. **update_coordinate_param** - 修改坐标系单个参数值（直接传值）
2. **update_coordinate_param_from_r** - 修改坐标系单个参数值（从R寄存器读取）
3. **update_coordinate_from_pr** - 从PR寄存器读取值更新整个坐标系

## 本地开发环境配置

### Python 3.14 环境

如果需要在本地完整测试，需要安装以下依赖：

1. **安装SDK**（已完成）：
   ```bash
   py -3.14 -m pip install "Python_v1.7.1.3\Agilebot.Robot.SDK.A-1.7.1.3+ca90c030.20250703-py3-none-any.whl"
   ```

2. **安装依赖**（已完成大部分）：
   ```bash
   py -3.14 -m pip install protobuf protocol requests google APScheduler setuptools aenum pytest paramiko
   ```

3. **安装pynng**（需要编译工具）：
   - 如果只需要IDE不报错，可以忽略此步骤
   - 如果需要完整本地测试，需要安装 [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - 然后运行：`py -3.14 -m pip install pynng`

### IDE配置

已创建以下配置文件来抑制导入警告：

- `pyrightconfig.json` - 配置Pyright/Pylance忽略缺失导入
- `.vscode/settings.json` - 配置VSCode Python分析器

**注意**：这些警告不影响插件在机器人系统中的运行，因为插件系统环境已包含所有依赖。

## 使用说明

详细使用说明请参考 [使用说明.md](使用说明.md)

### 快速开始

**在机器人编程界面中使用 CALL_SERVICE 指令：**

1. **修改坐标系单个参数（直接值）：**
   ```
   CALL_SERVICE CoordinateModifier.update_coordinate_param
     coord_type = "TF"
     coordinate_id = 1
     param_index = 1
     value = 100.5
   ```

2. **修改坐标系单个参数（从R寄存器）：**
   ```
   CALL_SERVICE CoordinateModifier.update_coordinate_param_from_r
     coord_type = "UF"
     coordinate_id = 2
     param_index = 4
     r_id = 5
   ```

3. **从PR寄存器更新整个坐标系：**
   ```
   CALL_SERVICE CoordinateModifier.update_coordinate_from_pr
     coord_type = "TF"
     coordinate_id = 1
     pr_id = 5
   ```

### 参数说明

- **coord_type**: "TF"（工具坐标系）或 "UF"（用户坐标系）
- **coordinate_id**: 坐标系索引ID，范围1-30（0是基础坐标系不可修改）
- **param_index**: 参数编号，1-6（1=X, 2=Y, 3=Z, 4=A, 5=B, 6=C）
- **value**: 要设置的值（坐标单位：mm，角度单位：度，精度：小数点后三位）
- **r_id**: R寄存器编号
- **pr_id**: PR寄存器编号

## 打包插件

运行打包脚本生成可导入的插件包：

```bash
python pack_plugin.py
```

打包后会生成 `CoordinateModifier_v0.1_YYYYMMDD.gbtapp` 文件（tar.gz格式，gzip压缩），可以直接导入到机器人系统中。

**注意**：.gbtapp 文件必须是 tar.gz 格式（gzip压缩），不能是 zip 格式。

## 文件结构

```
CoordinateModifier/
├── config.json                      # 插件配置文件
├── CoordinateModifier.py           # 主程序文件
├── pack_plugin.py                   # 打包脚本
├── pyrightconfig.json               # Pyright配置（抑制导入警告）
├── .vscode/
│   └── settings.json                # VSCode配置
├── README.md                        # 本文件
└── CoordinateModifier_v0.1_*.gbtapp   # 打包后的插件文件（可导入机器人）
```

