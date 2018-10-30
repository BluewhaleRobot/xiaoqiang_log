#!/usr/bin/env python
# encoding=utf-8

import json
import time

import pymongo
import rospy
import web
from bson import json_util
from pymongo import MongoClient
import threading

c = MongoClient()
db = c["xiaoqiang_log_server"]

urls = (
    '/', 'index'
)


class index:

    def GET(self):
        user_data = web.input()
        if not user_data.has_key("id") or not user_data.has_key("collection"):
            return json.dumps({
                "status": "error",
                "description": "id and collection is required"
            }, indent=4)

        # 查找到最新的时间戳
        record = db[user_data.collection].find_one({"id": user_data.id}, sort=[
            ("timestamp", pymongo.DESCENDING)])
        return json.dumps(record, default=json_util.default)

    def POST(self):
        data = web.data()
        try:
            data = json.loads(data)
        except Exception:
            data = None
        if data is None:
            return json.dumps({
                "status": "error",
                "description": "not a valid json format"
            })

        inserted_records = []
        for received_record in data:
            # 检查数据格式
            if "timestamp" not in received_record or "collection" not in received_record or "record" not in received_record:
                continue
            if "id" not in received_record["record"]:
                continue
            # 查找到最新的时间戳
            db_record = db[received_record["collection"]].find_one({"id": received_record["record"]["id"]}, sort=[
                ("timestamp", pymongo.DESCENDING)])
            # 收到数据并不比本地数据新
            if db_record is not None and db_record["timestamp"] > received_record["timestamp"]:
                continue
            # 保存数据
            received_record["record"]["timestamp"] = received_record["timestamp"]
            db[received_record["collection"]].insert(received_record["record"])
            inserted_records.append(received_record["record"])
        return json.dumps(inserted_records, indent=4, default=json_util.default)


if __name__ == "__main__":
    rospy.init_node("xiaoqiang_log_remote")
    app = web.application(urls, globals())
    threading._start_new_thread(app.run, ())
    while not rospy.is_shutdown():
        time.sleep(1)
