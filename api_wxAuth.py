# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  通过微信官方接口，获取OpenId
  @Version: 1.0
  @Author: lordli
  @Date: 2023-3-21
  @Update:
        1.0 构建基础服务
"""
import json
import requests
from fastapi import APIRouter
from pydantic import BaseModel
from configparser import ConfigParser

router = APIRouter()

class WxAuthRequest(BaseModel):
    code: str

# 读取配置文件
config = ConfigParser()
config.read(r'config.ini', encoding='utf-8')

def getOpenId(code):
    appid = config.get('wechat', 'appid')
    secret = config.get('wechat', 'secret')
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'.format(appid,secret,code)
    req = requests.get(url)
    data = json.loads(req.text)
    # 包装返回数据以匹配前端期望的结构
    return {
        "openid": data
    }

@router.put("/wxAuth/")
async def wx_login(request: WxAuthRequest):
    """
    微信小程序登录，获取OpenId
    """
    return getOpenId(request.code)
