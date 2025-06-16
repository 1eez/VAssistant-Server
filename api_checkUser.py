# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  检查用户信息接口
  @Version: 1.0
  @Author: lordli
  @Date: 2025-6-16
  @Update:
        1.0 构建基础服务
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class CheckUserRequest(BaseModel):
    openid: str

def checkUser(openid: str):
    # 构建返回的用户检查结果，模拟数据库查询结果
    result = {
        "checkUserResult": {
            "openid": openid,
            "vip": 1,
            "nickName": "尊贵用户",
            "balanceAmount": 99,
            "freeTry": 0,
            "usedToken3": 0,
            "usedToken4": 0,
            "sysContent3": "你是一个得力的助手",
            "sysContent4": "你是一个得力的助手",
            "temperature3": 1,
            "temperature4": 1,
            "status": "ok"
        }
    }
    return result

@router.put("/checkUser/")
async def check_user(request: CheckUserRequest):
    """
    检查用户信息
    """
    return checkUser(request.openid)