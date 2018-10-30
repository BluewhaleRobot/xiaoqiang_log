#!/usr/bin/env python
# encoding=utf-8

from xiaoqiang_log.msg import LogRecord
import rospy
import time
import json
from pymongo import MongoClient
from bson import json_util

if __name__ == "__main__":
    rospy.init_node("xiaoqiang_logger_client")
    # reset database
    c = MongoClient()
    db = c[rospy.get_param("~database_name", "xiaoqiang_log")]
    db["debug"].drop()
    # pub record to logger
    pub = rospy.Publisher("/xiaoqiang_log", LogRecord, queue_size=10)
    time.sleep(1)
    record = LogRecord()
    record.collection_name = "debug"
    record.stamp = rospy.Time.now()
    record.record = json.dumps({
        "hello": "world",
    }, indent=4)
    pub.publish(record)
    time.sleep(1)
    if db["debug"].find_one() is None:
        rospy.logerr("No record found")
    else:
        rospy.loginfo(json.dumps(db["debug"].find_one(),
                              indent=4, default=json_util.default))
    while not rospy.is_shutdown():
        time.sleep(1)
        record.stamp = rospy.Time.now()
        pub.publish(record)
