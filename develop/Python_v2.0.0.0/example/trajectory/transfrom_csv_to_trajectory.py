#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: CSV文件与轨迹文件转换功能使用示例 / Example of the use of the CSV file and trajectory file conversion function
"""
import os
import time
from pathlib import Path

from Agilebot import ROBOT_TMP, Arm, FileManager, StatusCodeEnum, TransformStatusEnum

current_path = Path(__file__).parent
file_path = "test.csv"
controller_ip = "10.27.1.254"

# [ZH] 连接文件管理服务
# [EN] Connect to the file management service
file_manager = FileManager(controller_ip)

# [ZH] 上传其他文件
# [EN] Upload other files
ret = file_manager.upload(str(current_path / file_path), ROBOT_TMP, True)
if ret == StatusCodeEnum.OK:
    print("上传文件成功 / Upload file successful")
else:
    print(f"上传文件失败，错误代码 / Upload file failed, error code: {ret.errmsg}")
    exit(1)

# [ZH] 初始化捷勃特机器人
# [EN] Initialize the robot
arm = Arm()
# [ZH] 连接捷勃特机器人
# [EN] Connect to the robot
ret = arm.connect(controller_ip)
# [ZH] 检查是否连接成功
# [EN] Check if the connection is successful
if ret == StatusCodeEnum.OK:
    print("机器人连接成功 / Robot connected successfully")
else:
    print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)

# [ZH] 转换CSV到轨迹文件
# [EN] Transform CSV to trajectory file
file_dir, ret = arm.trajectory.transform_csv_to_trajectory(file_path, io_flag="1")
if ret == StatusCodeEnum.OK:
    print("转换CSV到轨迹文件成功 / Transform CSV to trajectory file successful")
else:
    print(f"转换CSV到轨迹文件失败，错误代码 / Transform CSV to trajectory file failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
assert file_dir != None

start_time = time.time()
while True:
    status, ret = arm.trajectory.check_transform_status(os.path.basename(file_dir))
    if ret == StatusCodeEnum.OK:
        print("检查转换状态成功 / Check transform status successful")
    else:
        print(f"检查转换状态失败，错误代码 / Check transform status failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)
    print(f"status: {status}")
    if status == TransformStatusEnum.TRANSFORM_SUCCESS or status == TransformStatusEnum.TRANSFORM_FAILED:
        break
    time.sleep(2)
    if time.time() - start_time > 60:
        break

# [ZH] 检查转换状态
# [EN] Check transform status
status, ret = arm.trajectory.check_transform_status(os.path.basename(file_dir))
if ret == StatusCodeEnum.OK:
    print("检查转换状态成功 / Check transform status successful")
else:
    print(f"检查转换状态失败，错误代码 / Check transform status failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
assert status == TransformStatusEnum.TRANSFORM_NOT_FOUND
