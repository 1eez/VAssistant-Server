#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单轮对话聊天接口 -- 基于智谱AI GLM-4-Flash
@Version: 1.0
@Author: lordli
@Date: 2025-06-09
@Description: 提供单轮对话聊天功能，配合前端小程序使用
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from common_ai_chat import chat_with_ai
from configparser import ConfigParser
import logging
import time

# 系统提示和参数配置常量
FUNCTION_CONFIGS = {
    'translate2En': {
        'system_prompt': "I want you to act as an English translator, spelling corrector and improver. I will speak to you in any language and you will detect the language, translate it and answer in the corrected and improved version of my text, in English. I want you to replace my simplified A0-level words and sentences with more beautiful and elegant, upper level English words and sentences. Keep the meaning same, but make them more literary. I want you to only reply the correction, the improvements and nothing else, do not write explanations.",
        'temperature': 0.8
    },
    'translate2Ch': {
        'system_prompt': "你化身为中文专业翻译与润色大师。无论我采用何种语言，你务必迅速辨别，并对其进行精准、流畅、高雅的中文翻译和回复。望保持原意不变，又不失文学品味。请仅回复翻译结果，不要写出解释。",
        'temperature': 0.8
    },
    'dianping': {
        'system_prompt': "你作为喜欢赞誉和表扬的人。请对如下内容做出点评，语言风格生动、活泼、有趣，尽量补充更多细节。例如：用户输入：乐喜棋牌室。你的回答：【乐喜棋牌室体验超棒！】\n环境干净整洁，麻将机灵敏流畅，包厢私密性强，隔音效果很棒，完全沉浸式搓麻！服务热情周到，茶水零食随时供应，老板还会主动帮忙调空调温度，细节满分～最近新换了舒适座椅，久坐不累，牌友们都夸赞。周末人很多，建议提前预约，但等待区也有茶饮招待，体验很贴心。价格透明合理，还会不定期送小福利，绝对是附近麻将爱好者的首选！强烈推荐给喜欢休闲聚会的朋友们～",
        'temperature': 1.5,
        'max_tokens': 200
    }
}

# 默认配置
DEFAULT_SYSTEM_PROMPT = "你是一个有用的AI助手，请用中文回答用户的问题。"

# 读取配置文件
config = ConfigParser()
config.read(r'config.ini', encoding='utf-8')

router = APIRouter()

class ChatSingle3Request(BaseModel):
    function: str
    openid: str
    userInputStr: str

def get_user_info(openid: str):
    """
    获取用户信息（模拟数据库查询）
    """
    # 这里应该查询数据库获取用户信息
    # 为了演示，返回模拟数据
    return {
        "exists": True,
        "vip": 1,
        "balance": 99,
        "freeTry": 0
    }

def check_user_balance(openid: str):
    """
    检查用户余额
    """
    user_info = get_user_info(openid)
    if not user_info["exists"]:
        return False, "noUser"
    
    if user_info["balance"] <= 0 and user_info["freeTry"] <= 0:
        return False, "noMoney"
    
    return True, "ok"

def generate_session_id():
    """
    生成会话ID（单轮对话也需要返回sessionId）
    """
    return int(time.time())

@router.put("/chatSingle3/")
async def chat_single3(request: ChatSingle3Request):
    """
    单轮对话聊天接口
    """
    try:
        # 检查用户状态
        balance_ok, balance_status = check_user_balance(request.openid)
        if not balance_ok:
            if balance_status == "noUser":
                return {
                    "chatResult": {
                        "status": "noUser",
                        "sessionId": generate_session_id()
                    }
                }
            elif balance_status == "noMoney":
                return {
                    "chatResult": {
                        "status": "noMoney",
                        "sessionId": generate_session_id()
                    }
                }
        
        # 检查用户输入
        if not request.userInputStr or request.userInputStr.strip() == "":
            return {
                "chatResult": {
                    "status": "noSessionWord",
                    "sessionId": generate_session_id()
                }
            }
        
        # 根据function参数设置不同的系统提示和参数
        if request.function in FUNCTION_CONFIGS:
            config_data = FUNCTION_CONFIGS[request.function]
            system_prompt = config_data['system_prompt']
            temperature = config_data['temperature']
            # 如果配置中指定了max_tokens，则使用指定的值
            function_max_tokens = config_data.get('max_tokens')
        else:
            # 使用默认配置
            system_prompt = DEFAULT_SYSTEM_PROMPT
            temperature = config.getfloat('zhipu', 'temperature', fallback=1.0)
            function_max_tokens = None
        
        # 构建单轮对话消息
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": request.userInputStr
            }
        ]
        
        # 调用AI接口
        try:
            # 从配置文件读取AI参数
            model = config.get('zhipu', 'model', fallback='glm-4-flash')
            default_max_tokens = config.getint('zhipu', 'max_completion_tokens', fallback=1000)
            
            # 如果function配置中指定了max_tokens，则使用指定的值，否则使用默认值
            max_tokens = function_max_tokens if function_max_tokens is not None else default_max_tokens
            
            ai_response = chat_with_ai(
                messages=messages,
                model=model,
                temperature=temperature,  # 使用根据function动态设置的temperature
                max_tokens=max_tokens
            )
            
            return {
                "chatResult": {
                    "status": "OK",
                    "GPTmsg": ai_response,
                    "sessionId": generate_session_id()
                }
            }
            
        except Exception as ai_error:
            logging.error(f"AI调用失败: {ai_error}")
            return {
                "chatResult": {
                    "status": "error",
                    "errMsg": f"AI服务暂时不可用: {str(ai_error)}",
                    "sessionId": generate_session_id()
                }
            }
    
    except Exception as e:
        logging.error(f"chatSingle3接口异常: {e}")
        return {
            "chatResult": {
                "status": "error",
                "errMsg": f"系统错误: {str(e)}",
                "sessionId": generate_session_id()
            }
        }