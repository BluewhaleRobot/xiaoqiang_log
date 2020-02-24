#!/usr/bin/env python
# encoding=utf-8

import json
import time

import pymongo
import web
from bson import json_util
from pymongo import MongoClient
import threading
import requests
from functools import lru_cache

c = MongoClient()
db = c["xiaoqiang_log_server"]

urls = (
    '/', 'index'
)


class index:

    def GET(self):
        user_data = web.input()
        if "id" not in user_data or "collection" not in user_data:
            return json.dumps({
                "status": "error",
                "description": "id and collection is required"
            }, indent=4)

        # 查找到最新的时间戳
        record = db[user_data.collection].find_one({"id": user_data.id}, sort=[
            ("timestamp", pymongo.DESCENDING)])
        return json.dumps(record, default=json_util.default)

    def POST(self):
        data = web.data().decode("utf-8")
        try:
            data = json.loads(data)
        except Exception as e:
            print(e)
            data = None
        if data is None:
            return json.dumps({
                "status": "error",
                "description": "not a valid json format"
            })

        inserted_records = []
        timestamps = {}
        for received_record in data:
            # 检查数据格式
            if "timestamp" not in received_record or "collection" not in received_record or "record" not in received_record:
                continue
            if "id" not in received_record["record"]:
                continue
            # 查找到最新的时间戳
            if received_record["collection"] not in timestamps:
                db_record = db[received_record["collection"]].find_one({"id": received_record["record"]["id"]}, sort=[
                    ("timestamp", pymongo.DESCENDING)])
                if db_record is not None:
                    timestamps[received_record["collection"]] = db_record["timestamp"]
            # 收到数据并不比本地数据新
            if received_record["collection"] in timestamps and timestamps[received_record["collection"]] > received_record["timestamp"]:
                continue
            # 保存数据
            received_record["record"]["timestamp"] = received_record["timestamp"]
            received_record["record"]["ip"] = web.ctx.env.get('HTTP_X_FORWARDED_FOR')
            received_record["record"]["location"] = self.get_phy_addr(received_record["record"]["ip"])
            db[received_record["collection"]].insert(received_record["record"])
            inserted_records.append(received_record["record"])
        return json.dumps(inserted_records, indent=4, default=json_util.default)

    @lru_cache(maxsize=1024*1024)
    def get_phy_addr(self, ip):
        try:
            req = requests.post("http://xiaoqiang.bwbot.org/ips", data={"ip": ip})
        except Exception:
            return ""
        if req.json()[0] is None:
            return ""
        return req.json()[0]

if __name__ == "__main__":
    app = web.application(urls, globals())
    threading._start_new_thread(app.run, ())
    while True:
        time.sleep(1)
