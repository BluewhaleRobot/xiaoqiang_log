#!/usr/bin/env python
# encoding=utf-8

import json
import re
import time

import requests
import rospy
from pymongo import MongoClient
from xiaoqiang_log.msg import LogRecord

c = MongoClient()
database_name = rospy.get_param("~database_name", "xiaoqiang_log")
db = c[database_name]


def get_id(sharplink_log):
    log_file = open(sharplink_log)
    contents = log_file.read()
    log_file.close()
    mid_search = re.search(r"[0-9]+,\sID:\s(?P<id>[0-9A-F]{76})", contents)
    mid = mid_search.group("id")
    return mid


def insert_log_record(record):
    db[record.collection_name].insert({
        "timestamp": record.stamp.to_nsec() / 1000 / 1000,
        "record": json.loads(record.record)
    })
    try:
        server_url = rospy.get_param("~server_url", "http://127.0.0.1:9999")
        sharplink_log = rospy.get_param("~sharplink_log", "")
        if sharplink_log == "":
            return
        res = requests.get(server_url, params={
            "id": get_id(sharplink_log),
            "collection": record.collection_name,
        }, timeout=5)
        res = json.loads(res.content.decode("utf-8"))
        timestamp = 0
        if res is not None:
            timestamp = res["timestamp"]
        # query data need to send
        data_to_send = list(db[record.collection_name].find(
            {"timestamp": {"$gt": timestamp}}, {"_id": 0}
        ))
        if len(data_to_send) == 0:
            return
        for data in data_to_send:
            data["collection"] = record.collection_name
            data["record"]["id"] = get_id(sharplink_log)
        # send data to server
        res = requests.post(server_url, json=data_to_send)
        res = json.loads(res.content.decode("utf-8"))
        if len(res) < len(data_to_send):
            rospy.logwarn("some records failed to insert")

    except Exception as e:
        rospy.loginfo("Connect to remote server failed")
        rospy.loginfo(e)


if __name__ == "__main__":
    rospy.init_node("xiaoqiang_logger_node")
    sub = rospy.Subscriber("/xiaoqiang_log", LogRecord,
                           insert_log_record, queue_size=10)
    while not rospy.is_shutdown():
        time.sleep(1)
