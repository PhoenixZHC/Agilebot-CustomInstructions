#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 文件操作, 上传下载示例 / Example of file operation, upload and download
"""
from pathlib import Path

from Agilebot import ROBOT_TMP, TRAJECTORY, TRAJECTORY_CSV, USER_PROGRAM, Arm, FileManager, StatusCodeEnum

current_path = Path(__file__)
path = str(current_path)

# [ZH] 连接文件管理服务
# [EN] Connect to the file management service
file_manager = FileManager("10.27.1.254")

# [ZH] 上传其他文件
# [EN] Upload other files
tmp_file_path = path.replace("file_manager.py", "test.csv")
ret = file_manager.upload(tmp_file_path, ROBOT_TMP, True)
if ret == StatusCodeEnum.OK:
    print("文件上传成功 / File upload successful")
else:
    print(f"文件上传失败，错误代码 / File upload failed, error code: {ret.errmsg}")
    exit(1)

# [ZH] 上传程序
# [EN] Upload a program
prog_file_path = path.replace("file_manager.py", "test_prog")
ret = file_manager.upload(prog_file_path, USER_PROGRAM, True)
if ret == StatusCodeEnum.OK:
    print("程序上传成功 / Program upload successful")
else:
    print(f"程序上传失败，错误代码 / Program upload failed, error code: {ret.errmsg}")
    exit(1)

# [ZH] 上传轨迹
# [EN] Upload a trajectory
trajectory_file_path = path.replace("file_manager.py", "test_torque.trajectory")
ret = file_manager.upload(trajectory_file_path, TRAJECTORY, True)
if ret == StatusCodeEnum.OK:
    print("轨迹上传成功 / Trajectory upload successful")
else:
    print(f"轨迹上传失败，错误代码 / Trajectory upload failed, error code: {ret.errmsg}")
    exit(1)

# [ZH] 搜索文件
# [EN] Search for files
file_list = list()
ret = file_manager.search("test.csv", file_list)
if ret == StatusCodeEnum.OK:
    print("文件搜索成功 / File search successful")
else:
    print(f"文件搜索失败，错误代码 / File search failed, error code: {ret.errmsg}")
    exit(1)
print("搜索文件：", file_list)

# [ZH] 下载文件
# [EN] Download a file
download_file_path = path.replace("file_manager.py", "download")
ret = file_manager.download("test_torque", download_file_path, file_type=TRAJECTORY)
if ret == StatusCodeEnum.OK:
    print("文件下载成功 / File download successful")
else:
    print(f"文件下载失败，错误代码 / File download failed, error code: {ret.errmsg}")
    exit(1)

# [ZH] 删除文件
# [EN] Delete a file
ret = file_manager.delete("test_torque.trajectory", TRAJECTORY)
if ret == StatusCodeEnum.OK:
    print("文件删除成功 / File delete successful")
else:
    print(f"文件删除失败，错误代码 / File delete failed, error code: {ret.errmsg}")
    exit(1)
