#!python
"""
 Copyright © 2016 Agilebot Robotics Ltd. All rights reserved.
 Instruction: SubPub使用示例 / SubPub usage example
"""

import asyncio
import logging

from Agilebot import Arm, IOTopicType, RegTopicType, RobotTopicType, StatusCodeEnum

# 配置日志 / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def message_handler(message):
    """
    消息处理函数 / Message handler function

    :param message: 接收到的消息字典 / Received message dictionary
    """
    logger.info(f"收到消息 / Received message: {message}")


async def main():
    """
    主函数，演示SubPub的使用 / Main function demonstrating SubPub usage
    """
    # 创建Arm实例 / Create Arm instance
    arm = Arm()

    # 连接到控制器 / Connect to controller
    ret = arm.connect("192.168.110.100")
    if ret != StatusCodeEnum.OK:
        logger.error(f"连接失败 / Connection failed: {ret}")
        return

    logger.info("Arm连接成功 / Arm connected successfully")

    try:
        # 连接WebSocket / Connect WebSocket
        ret = await arm.sub_pub.connect()
        if ret != StatusCodeEnum.OK:
            logger.error(f"WebSocket连接失败 / WebSocket connection failed: {ret}")
            return

        logger.info("WebSocket连接成功 / WebSocket connected successfully")



        # 订阅IO信号 / Subscribe to IO signals
        io_list = [(IOTopicType.DI, 1), (IOTopicType.DO, 1)]

        ret = await arm.sub_pub.subscribe_io(io_list, frequency=200)
        if ret != StatusCodeEnum.OK:
            logger.error(f"订阅IO失败 / Failed to subscribe to IO: {ret}")
            return

        logger.info("IO订阅成功 / IO subscription successful")

        # 单次接收消息示例 / Single message receive example
        logger.info("尝试单次接收消息 / Attempting single message receive")
        try:
            # 设置超时 / Set timeout
            message, ret = await asyncio.wait_for(arm.sub_pub.receive(), timeout=5.0)
            if ret == StatusCodeEnum.OK:
                logger.info(f"单次接收消息成功 / Single message receive successful: {message}")
            else:
                logger.error(f"单次接收消息失败 / Single message receive failed: {ret}")
        except asyncio.TimeoutError:
            logger.warning("接收消息超时 / Message receive timeout")

        # 启动消息接收 / Start message receiving
        ret = await arm.sub_pub.start_receiving(message_handler) 
        if ret != StatusCodeEnum.OK:
            logger.error(f"启动消息接收失败 / Failed to start message receiving: {ret}")
            return

        logger.info("开始接收消息 / Started receiving messages")

        # 运行一段时间 / Run for a while
        logger.info("运行10秒钟... / Running for 10 seconds...")
        await asyncio.sleep(10)

    except Exception as e:
        logger.error(f"运行过程中发生错误 / Error occurred during execution: {str(e)}")

    finally:
        # 断开连接 / Disconnect
        await arm.sub_pub.disconnect()
        arm.disconnect()
        logger.info("连接已断开 / Connection disconnected")


if __name__ == "__main__":
    # 运行异步主函数 / Run async main function
    asyncio.run(main())
