# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  添加用户信息接口
  @Version: 1.0
  @Author: lordli
  @Date: 2025-6-16
  @Update:
        1.0 构建基础服务
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Union

router = APIRouter()

class UserData(BaseModel):
    openid: str
    brand: Optional[str] = None
    model: Optional[str] = None
    wxVer: Optional[str] = None
    wxLang: Optional[str] = None
    osVer: Optional[str] = None
    platform: Optional[str] = None
    wxFontSize: Optional[Union[str, int]] = None
    deviceOrientation: Optional[str] = None
    batteryLevel: Optional[Union[str, int]] = None
    networkType: Optional[str] = None

def addUser(user_data: UserData):
    # 构建返回的用户数据结构
    result = {
        "addUserResult": {
            "userType": "vip",
            "userData": {
                "openid": user_data.openid,
                "nickName": "User",
                "mobileNo": None,
                "inviter": "Lord",
                "notice": 0,
                "HashPW": "",
                "balanceAmount": 99,
                "batteryLevel": str(user_data.batteryLevel) if user_data.batteryLevel else "无",
                "brand": user_data.brand or "Unknown",
                "createDate": "",
                "deviceOrientation": user_data.deviceOrientation or "portrait",
                "freeTry": 0,
                "model": user_data.model or "Unknown",
                "networkType": user_data.networkType or "wifi",
                "osVer": user_data.osVer or "Unknown",
                "platform": user_data.platform or "unknown",
                "settings": "E",
                "topupAmount": 99,
                "vip": 1,
                "wxFontSize": str(user_data.wxFontSize) if user_data.wxFontSize else "无",
                "wxLang": user_data.wxLang or "zh",
                "wxVer": user_data.wxVer or "Unknown"
            }
        }
    }
    return result

@router.put("/addUser/")
async def add_user(user_data: UserData):
    """
    添加用户信息
    """
    return addUser(user_data)