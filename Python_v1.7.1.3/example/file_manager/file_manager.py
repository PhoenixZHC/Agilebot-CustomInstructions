#!python
from Agilebot.IR.A.arm import Arm
from Agilebot.IR.A.status_code import StatusCodeEnum
from Agilebot.IR.A.file_manager import FileManager
from Agilebot.IR.A.file_manager import TRAJECTORY_CSV, TRAJECTORY, ROBOT_TMP, USER_PROGRAM
from pathlib import Path

current_path = Path(__file__)
path = str(current_path)

# 连接文件管理服务
file_manager = FileManager("10.27.1.254")

# 上传其他文件
tmp_file_path = path.replace("file_manager.py", "test.csv")
ret = file_manager.upload(tmp_file_path, ROBOT_TMP, True)
assert ret == StatusCodeEnum.OK

# 上传程序
prog_file_path = path.replace("file_manager.py", "test_prog")
ret = file_manager.upload(prog_file_path, USER_PROGRAM, True)
assert ret == StatusCodeEnum.OK

# 上传轨迹
trajectory_file_path = path.replace("file_manager.py", "test_torque.trajectory")
ret = file_manager.upload(trajectory_file_path, TRAJECTORY, True)
assert ret == StatusCodeEnum.OK

# 搜索文件
file_list = list()
ret = file_manager.search("test.csv", file_list)
assert ret == StatusCodeEnum.OK
print("搜索文件：", file_list)

# 下载文件
download_file_path = path.replace("file_manager.py", "download")
ret = file_manager.download("test_torque", download_file_path, file_type=TRAJECTORY)
assert ret == StatusCodeEnum.OK

# 删除文件
ret = file_manager.delete("test_torque.trajectory", TRAJECTORY)
assert ret == StatusCodeEnum.OK

