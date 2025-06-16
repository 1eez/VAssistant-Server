# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  获得小程序首页功能列表
  @Version: 1.0
  @Author: lordli
  @Date: 2023-5-6
  @Update:
        1.0 构建基础服务
"""
from fastapi import APIRouter

router = APIRouter()
def getFunctions():
    """获取功能配置数据"""
    baseConfig = {
        'naviConfig': [
        {
          'icon': '/images/navigator/icon-chat3.png',
          'title': '畅聊 3.5',
          'navigateMark': 'chat3',
          'Tag': 'hot'
        },
        {
          'icon': '/images/navigator/icon-chat4.png',
          'title': '畅聊 4.0',
          'navigateMark': 'chat4',
          'Tag': 'new'
        },
        {
          'icon': '/images/navigator/icon-dayi.png',
          'title': '答疑解惑',
          'navigateMark': 'queries',
          'Tag': 'hot'
        },
        {
          'icon': '/images/navigator/icon-law.png',
          'title': '婚姻法咨询',
          'navigateMark': 'hunyin_law',
          'Tag': 'new'
        },
        {
          'icon': '/images/navigator/icon-liao.png',
          'title': '寂寞陪聊',
          'navigateMark': 'lonely'
        },
        {
          'icon': '/images/navigator/icon-poem.png',
          'title': '吟游诗人',
          'navigateMark': 'poet'
        },
        {
          'icon': '/images/navigator/icon-zuoti.png',
          'title': 'Midjourney提示词',
          'navigateMark': 'MJPrompt'
        },
        {
          'icon': '/images/navigator/icon-dianping.png',
          'title': '写点评',
          'navigateMark': 'dianping'
        },
        {
          'icon': '/images/navigator/icon-kua.png',
          'title': '夸夸我',
          'navigateMark': 'kuakua'
        },
        {
          'icon': '/images/navigator/icon-zhong.png',
          'title': '中译英',
          'navigateMark': 'translate2En'
        },
        {
          'icon': '/images/navigator/icon-ying.png',
          'title': '英译中',
          'navigateMark': 'translate2Ch'
        }
        ],
        'labelConfig': {
          'label1': '用户名',
          'label2': '手机号码',
          'label3': '+86',
          'label4': '可用余额',
          'label5': '元',
          'label6': '已使用Token（3.5）',
          'label7': '已使用Token（4.0）',
          'label8': 'Token成本（3.5）',
          'label9': 'Token成本（4.0）',
          'label10': '为了方便称呼，请输入您的昵称',
          'label11': '（补充昵称可获得三次体验机会）',
          'label12': '昵称',
          'label13': '手机'
        }
      }
    
    return {'baseConfig': baseConfig}

@router.put("/getFunctions/")
async def get_functions():
    """
    获取小程序首页功能列表
    """
    return getFunctions()
