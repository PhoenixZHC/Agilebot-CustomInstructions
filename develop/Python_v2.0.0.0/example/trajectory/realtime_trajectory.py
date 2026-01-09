#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: 实时轨迹相关使用示例 / Example of real-time trajectory usage
"""
import enum
import logging
import time
from pathlib import Path
from typing import List

from Agilebot import Arm, MotionPose, RobotStatusEnum, ServoStatusEnum, StatusCodeEnum
from Agilebot.IR.A.common.const import *
from Agilebot.IR.A.controller_proto_pb2.message_type.motion_trajectory_pb2 import (
    TrajectoryPoint,
    TrajectorySegment,
    TrajIO,
)
from Agilebot.IR.A.real_time_trajectory.rt_trajectory import RealTimeTrajectory

TRA_SEG_LIMIT = 10
# 控制器IP
ARM_CONTROLLER_IP = "10.27.1.254"
current_path = Path(__file__).parent
# 轨迹文件名
file_path = "test_torque.trajectory"
TRAJECTORY_FILE = str(current_path / file_path)


class TrajectorySegCls:
    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__global_index = 0
        self.__segment_list = None

    @staticmethod
    def get_single_trajectory_point(trajectory_seg: List[str]) -> TrajectoryPoint:
        res = TrajectoryPoint()
        if len(trajectory_seg) < 24:
            return None
        res.position_list.data.extend([float(i) for i in trajectory_seg[:6]])
        res.velocity_list.data.extend([float(i) for i in trajectory_seg[6:12]])
        res.acceleration_list.data.extend([float(i) for i in trajectory_seg[12:18]])
        res.effort_list.data.extend([float(i) for i in trajectory_seg[18:24]])
        res.signal_list.data.extend([TrajIO(port=-1, value=0)])
        res.time_from_start.sec = 0
        res.time_from_start.nsec = 0
        return res

    @staticmethod
    def get_trajectory_segment(
        seq: int, last_fragment: bool, trajectory_point_list: List[TrajectoryPoint]
    ) -> TrajectorySegment:
        res = TrajectorySegment()
        res.point_list.data.extend(trajectory_point_list)
        res.total_points = len(trajectory_point_list)
        res.seq = seq
        res.last_fragment = 1 if last_fragment else 0
        res.trajectory_time_stamp.sec = 0
        res.trajectory_time_stamp.nsec = 0
        return res

    @staticmethod
    def gctrl_statuset_trajectory_segment(
        seq: int, last_fragment: bool, trajectory_point_list: List[TrajectoryPoint]
    ) -> TrajectorySegment:
        res = TrajectorySegment()
        res.point_list.data.extend(trajectory_point_list)
        res.total_points = len(trajectory_point_list)
        res.seq = seq
        res.last_fragment = 1 if last_fragment else 0
        res.trajectory_time_stamp.sec = 0
        res.trajectory_time_stamp.nsec = 0
        return res

    def get_trajectory_segment_list(self) -> List[TrajectorySegment]:
        res = []
        with open(self.__file_path, "r") as f:
            cursor = 0
            tem_trajectory_point_list = []
            length = 0
            for line in f:
                length += 1
            f.seek(0)
            seq = 0
            for index, line in enumerate(f):
                single_trajectory_point = self.get_single_trajectory_point(line.split(" "))
                if single_trajectory_point is None:
                    continue
                cursor += 1
                tem_trajectory_point_list.append(single_trajectory_point)
                if cursor == TRA_SEG_LIMIT:
                    cursor = 0
                    # 4个点为一个seg
                    seq = int((index - 2) / TRA_SEG_LIMIT)
                    res.append(self.get_trajectory_segment(seq, index == length - 1, tem_trajectory_point_list))
                    tem_trajectory_point_list.clear()
            if len(tem_trajectory_point_list) > 0:
                seq += 1
                res.append(self.get_trajectory_segment(seq, True, tem_trajectory_point_list))
        return res

    def repeat_get_trajectory_segment_list(self) -> List[TrajectorySegment]:
        if self.__segment_list is not None:
            return self.__segment_list
        res = []
        with open(self.__file_path, "r") as f:
            cursor = 0
            tem_trajectory_point_list = []
            for index, line in enumerate(f):
                single_trajectory_point = self.get_single_trajectory_point(line.split(" "))
                if single_trajectory_point is None:
                    continue
                cursor += 1
                tem_trajectory_point_list.append(single_trajectory_point)
                if cursor == TRA_SEG_LIMIT:
                    cursor = 0
                    # 4个点为一个seg
                    res.append(self.get_trajectory_segment(self.__global_index, False, tem_trajectory_point_list))
                    self.__global_index += 1
                    tem_trajectory_point_list.clear()
            if len(tem_trajectory_point_list) > 0:
                res.append(self.get_trajectory_segment(self.__global_index, False, tem_trajectory_point_list))
                self.__global_index += 1
        self.__segment_list = res
        return res


def is_arm_idle(arm) -> bool:
    while True:
        ctrl_status, ret = arm.get_ctrl_status()
        if ret != StatusCodeEnum.OK:
            assert 0 == 1
        logging.info(f"ctrl_status arm: {ctrl_status}")
        robot_status, ret = arm.get_robot_status()
        if ret != StatusCodeEnum.OK:
            assert 0 == 1
        logging.info(f"robot_status arm: {robot_status}")
        servo_status, ret = arm.get_servo_status()
        if ret != StatusCodeEnum.OK:
            assert 0 == 1
        logging.info(f"servo status arm: {servo_status}")
        if robot_status == RobotStatusEnum.ROBOT_IDLE and servo_status == ServoStatusEnum.SERVO_IDLE:
            break
        time.sleep(2)
    return True


if __name__ == "__main__":
    # 一次正常的实时轨迹下发过程
    arm = Arm()
    ret = arm.connect(arm_controller_ip=ARM_CONTROLLER_IP)
    if ret == StatusCodeEnum.OK:
        print("机器人连接成功 / Robot connected successfully")
    else:
        print(f"机器人连接失败，错误代码 / Robot connection failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)

    # 创建实时轨迹对象
    rtt: RealTimeTrajectory = RealTimeTrajectory(ARM_CONTROLLER_IP)
    # 0、确保当前已经退出实时轨迹控制模式
    ret = rtt.exit_trajectory_control()
    if ret == StatusCodeEnum.OK:
        print("退出轨迹控制模式成功 / Exit trajectory control mode successful")
    else:
        print(f"退出轨迹控制模式失败，错误代码 / Exit trajectory control mode failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)

    # 1、reset机器人
    ret = arm.servo_reset()
    if ret == StatusCodeEnum.OK:
        print("伺服重置成功 / Servo reset successful")
    else:
        print(f"伺服重置失败，错误代码 / Servo reset failed, error code: {ret.errmsg}")
        arm.disconnect()
        exit(1)

    # 2、等待机器人进入IDLE状态
    is_arm_idle(arm)

    # 3、将机器人移动到轨迹初始点位
    motion_pose = MotionPose()
    motion_pose.pt = const.JOINT
    # test_torque.tra
    motion_pose.joint.j1 = 25.85
    motion_pose.joint.j2 = 0.98
    motion_pose.joint.j3 = -5.67
    motion_pose.joint.j4 = -8.83
    motion_pose.joint.j5 = 31.52
    motion_pose.joint.j6 = 38.00

    ret_code = arm.motion.move_to_pose(motion_pose, const.MOVE_JOINT)
    if ret_code == StatusCodeEnum.OK:
        print("移动到初始位姿成功 / Move to initial pose successful")
    else:
        print(f"移动到初始位姿失败，错误代码 / Move to initial pose failed, error code: {ret_code.errmsg}")
        arm.disconnect()
        exit(1)

    # 等待机器人进入IDLE状态
    is_arm_idle(arm)

    # 4、进入实时轨迹控制模式
    ret_code = rtt.enter_trajectory_control()
    if ret_code == StatusCodeEnum.OK:
        print("进入轨迹控制模式成功 / Enter trajectory control mode successful")
    else:
        print(f"进入轨迹控制模式失败，错误代码 / Enter trajectory control mode failed, error code: {ret_code.errmsg}")
        arm.disconnect()
        exit(1)
    try:
        points = TrajectorySegCls(TRAJECTORY_FILE).get_trajectory_segment_list()
        for i in points:
            # 5.1、下发实时轨迹点位
            ret = rtt.send_trajectory(i)
            print(ret)
    except Exception as e:
        print(e)
        pass
    finally:
        # 等待机器人进入IDLE状态
        is_arm_idle(arm)
        # 6、退出实时轨迹控制模式
        ret = rtt.exit_trajectory_control()
if ret == StatusCodeEnum.OK:
    print("退出轨迹控制模式成功 / Exit trajectory control mode successful")
else:
    print(f"退出轨迹控制模式失败，错误代码 / Exit trajectory control mode failed, error code: {ret.errmsg}")
    arm.disconnect()
    exit(1)
