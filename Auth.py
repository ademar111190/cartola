#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json


def get_auth():
    file = open("config.txt", "r")
    data = file.read().split("\n")
    email = data[0].replace("email=", "")
    password = data[1].replace("password=", "")
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8'
    }
    data = json.dumps({
        "payload": {
            "email": email,
            "password": password,
            "serviceId": 464
        },
        "captcha": ""})
    response = requests.post('https://login.globo.com/api/authentication', headers=headers, data=data)
    auth = json.loads(response.content)
    return auth["glbId"]
