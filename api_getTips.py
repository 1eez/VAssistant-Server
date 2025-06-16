# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  获得welcome页面中，图片下面的跑马灯
  @Version: 1.0
  @Author: lordli
  @Date: 2023-5-6
  @Update:
        1.0 构建基础服务
"""
from fastapi import APIRouter

router = APIRouter()

def getTips():
    result = {
        'tips': {
            'tipsList':[
            {
              'text': '小程序版本升级，现在可无限制免费试用'
            },
            {
              'text': '为了防止消息丢失，退出前记得点击"全部复制"'
            },
            {
              'text': '如需更多功能，详询作者'
            }
            ]
        }
    }
    return result

@router.put("/getTips/")
async def get_tips():
    """
    获取欢迎页面的提示信息
    """
    return getTips()
