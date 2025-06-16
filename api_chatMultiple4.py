#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多轮对话聊天接口4 -- 基于智谱AI GLM-4-Flash
@Version: 1.0
@Author: lordli
@Date: 2025-06-09
@Description: 提供多轮对话聊天功能，配合前端小程序使用
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from common_ai_chat import chat_with_ai
from configparser import ConfigParser
import logging

# 系统提示和参数配置常量
FUNCTION_CONFIGS = {
    'chat4': {
        'system_prompt': "你是我的助理。",
        'temperature': 0.9
    }
}

# 默认配置
DEFAULT_SYSTEM_PROMPT = "你是一个有用的AI助手，请用中文回答用户的问题。"

# 读取配置文件
config = ConfigParser()
config.read(r'config.ini', encoding='utf-8')

router = APIRouter()

class ChatMultiple4Request(BaseModel):
    function: str
    openid: str
    sessionid: int
    userInputStr: str

# 模拟会话存储（实际项目中应使用数据库）
sessions = {}

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
        return False, "runOut"
    
    return True, "ok"

def get_session_messages(sessionid: int, openid: str):
    """
    获取会话历史消息
    """
    session_key = f"{openid}_{sessionid}"
    if session_key not in sessions:
        sessions[session_key] = []
    return sessions[session_key]

def save_session_message(sessionid: int, openid: str, role: str, content: str):
    """
    保存会话消息
    """
    session_key = f"{openid}_{sessionid}"
    if session_key not in sessions:
        sessions[session_key] = []
    
    sessions[session_key].append({
        "role": role,
        "content": content
    })
    
    # 限制会话历史长度，避免token过多
    if len(sessions[session_key]) > 20:
        sessions[session_key] = sessions[session_key][-20:]

def generate_new_session_id(openid: str):
    """
    生成新的会话ID
    """
    # 简单的会话ID生成逻辑
    import time
    return int(time.time())

@router.put("/chatMultiple4/")
async def chat_multiple4(request: ChatMultiple4Request):
    """
    多轮对话聊天接口4
    """
    try:
        # 检查用户状态
        balance_ok, balance_status = check_user_balance(request.openid)
        if not balance_ok:
            if balance_status == "noUser":
                return {
                    "chatResult": {
                        "status": "noUser",
                        "sessionId": request.sessionid
                    }
                }
            elif balance_status == "runOut":
                return {
                    "chatResult": {
                        "status": "runOut",
                        "sessionId": request.sessionid
                    }
                }
        
        # 检查用户输入
        if not request.userInputStr or request.userInputStr.strip() == "":
            return {
                "chatResult": {
                    "status": "noSessionWord",
                    "sessionId": request.sessionid
                }
            }
        
        # 获取或创建会话ID
        current_session_id = request.sessionid
        if current_session_id == 0:
            current_session_id = generate_new_session_id(request.openid)
        
        # 获取会话历史
        messages = get_session_messages(current_session_id, request.openid)
        
        # 添加系统提示（如果是新会话）
        if len(messages) == 0:
            # 根据function参数获取对应的系统提示
            config_info = FUNCTION_CONFIGS.get(request.function, {})
            system_prompt = config_info.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加用户消息
        messages.append({
            "role": "user",
            "content": request.userInputStr
        })
        
        # 调用AI接口
        try:
            # 从配置文件读取AI参数
            model = config.get('zhipu', 'model', fallback='glm-4-flash')
            # 根据function参数获取对应的温度设置
            config_info = FUNCTION_CONFIGS.get(request.function, {})
            temperature = config_info.get('temperature', config.getfloat('zhipu', 'temperature', fallback=1.0))
            max_tokens = config.getint('zhipu', 'max_completion_tokens', fallback=1000)
            
            ai_response = chat_with_ai(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # 保存用户消息和AI回复到会话历史
            save_session_message(current_session_id, request.openid, "user", request.userInputStr)
            save_session_message(current_session_id, request.openid, "assistant", ai_response)
            
            return {
                "chatResult": {
                    "status": "OK",
                    "GPTmsg": ai_response,
                    "sessionId": current_session_id
                }
            }
            
        except Exception as ai_error:
            logging.error(f"AI调用失败: {ai_error}")
            return {
                "chatResult": {
                    "status": "error",
                    "errMsg": f"AI服务暂时不可用: {str(ai_error)}",
                    "sessionId": current_session_id
                }
            }
    
    except Exception as e:
        logging.error(f"chatMultiple4接口异常: {e}")
        return {
            "chatResult": {
                "status": "error",
                "errMsg": f"系统错误: {str(e)}",
                "sessionId": request.sessionid
            }
        }