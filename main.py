# -*- coding: utf-8 -*-

from hashlib import md5
import random
import json
import os
import sys

import re
parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, 'lib'))
sys.path.append(os.path.join(parent_folder_path, 'plugin'))

from flowlauncher import FlowLauncher
import pyperclip
import requests



config_file = os.path.join(os.getcwd(), "config.json") 


class Translate(FlowLauncher):

    def write_config(self, data):  
        with open(config_file, "w") as f:
            f.write(json.dumps(data))

    def key(self):
        if not os.path.exists(config_file):
            self.write_config({"appid": "", "appkey": ""})
        with open(config_file, "r") as f:
            json_data = json.loads(f.read())

        appid, appkey = json_data.get("appid"), json_data.get("appkey")
        return appid, appkey


    def check(self, appid, appkey):
        # print(appid, appkey)
        if appid and appkey:
            return True
        return False

    def translate(self, from_lang, to_lang, appid, query, appkey):
        # from_lang = 'zh'
        # to_lang = 'en'

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path
            # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(appid + query + str(salt) + appkey)

            # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang,
                    'to': to_lang, 'salt': salt, 'sign': sign}

            # Send request
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()

            # Show response
        trans_result = result.get("trans_result")
        return trans_result

    def error(self):
        return [
            {
                "Title": "输入错误! 请重新输入 appid 和 appkey 中间使用&符分割",
                "SubTitle": "Error",
                "IcoPath": "Images/app.png",
            }
        ]
    
    def query(self, query):
        appid, appkey = self.key()
        check_status = self.check(appid, appkey)
        if check_status:
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
            if re.findall('[\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b]',query):
                trans_result = self.translate('zh', 'en', appid, query, appkey)
            else:
                trans_result = self.translate('auto','zh', appid, query, appkey)
                
            if trans_result:
                for i in trans_result:
                    tran = i.get('dst')
            else:
                tran = "错误" if query else ""
            src = query if query else "请输入翻译内容"
            return [
                {
                    "Title": tran,
                    "SubTitle": src,
                    "IcoPath": "Images/app.png",
                    "JsonRPCAction": {
                        "method": "copy",
                        "parameters": [tran]
                    }
                }
            ]
        else:
            config_data = {"appid": "", "appkey": ""}
            if query:
                if "&" in str(query):
                    sdata = str(query).split("&")
                    if len(sdata) == 2:
                        appid, appkey = sdata
                        config_data["appid"] = appid
                        config_data["appkey"] = appkey
                        self.write_config(config_data)
                    else:    
                        return self.error()
                else:
                    return self.error()
            return [
                {
                "Title": "请输入 appid 和 appkey 中间使用&符分割",
                "SubTitle": "config",
                "IcoPath": "Images/app.png",
                    }
                        ]

    def copy(self, data):
        pyperclip.copy(data)


if __name__ == "__main__":
    Translate()
