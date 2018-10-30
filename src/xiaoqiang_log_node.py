#!/usr/bin/env python
# encoding=utf-8

import json
import time

import rospy
from pymongo import MongoClient
from xiaoqiang_log.msg import LogRecord

c = MongoClient()
database_name = rospy.get_param("database_name", "xiaoqiang_log")
db = c[database_name]


def insert_log_record(record):
    db[record.collection_name].insert({
        "timestamp": record.stamp.to_nsec() / 1000 / 1000,
        "record": json.loads(record.record)
    })


if __name__ == "__main__":
    rospy.init_node("xiaoqiang_logger_node")
    now = rospy.Time.now()
    print(now.to_nsec())
    sub = rospy.Subscriber("/xiaoqiang_log", LogRecord,
                           insert_log_record, queue_size=10)
    while not rospy.is_shutdown():
        time.sleep(1)
