#!/usr/bin/env python
#encoding=utf-8

import rospy
from xiaoqiang_log.msgs import LogRecord
import time

if __name__ == "__main__":
    print("test")
    rospy.init_node("xiaoqiang_logger_node")
    while not rospy.is_shutdown():
        time.sleep(1)
    print("test")