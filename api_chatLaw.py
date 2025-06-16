#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
法律咨询聊天接口 -- 基于智谱AI GLM-4-Flash
@Version: 1.0
@Author: lordli
@Date: 2025-06-09
@Description: 提供法律咨询聊天功能，配合前端小程序使用
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from common_ai_chat import chat_with_ai
from configparser import ConfigParser
import logging

# 系统提示和参数配置常量
FUNCTION_CONFIGS = {
    'law': {
        'system_prompt': "你是一个专业的法律顾问助手。请根据用户的问题提供准确、专业的法律建议和分析。在回答时，请分别提供：1. 直接回答用户问题的内容；2. 相关的法律条文或案例引用；3. 详细的法律分析。",
        'temperature': 0.7
    }
}

# 默认配置
DEFAULT_SYSTEM_PROMPT = "你是一个专业的法律顾问助手，请用中文回答用户的法律问题。"

# 读取配置文件
config = ConfigParser()
config.read(r'config.ini', encoding='utf-8')

router = APIRouter()

class ChatLegalRequest(BaseModel):
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
        return False, "runOut"
    
    return True, "ok"

def parse_ai_response(ai_response: str):
    """
    解析AI响应，提取ResultText、chosenText和analysisText
    """
    # 尝试按照特定格式解析AI响应
    lines = ai_response.split('\n')
    
    result_text = ai_response  # 默认整个响应作为ResultText
    chosen_text = ""  # 法律条文引用
    analysis_text = ""  # 法律分析
    
    # 简单的解析逻辑，可以根据实际需要调整
    current_section = "result"
    temp_chosen = []
    temp_analysis = []
    temp_result = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测是否是法律条文引用部分
        if any(keyword in line for keyword in ["法律条文", "相关法条", "法律依据", "引用", "条文"]):
            current_section = "chosen"
            continue
        # 检测是否是分析部分
        elif any(keyword in line for keyword in ["法律分析", "详细分析", "分析", "解释"]):
            current_section = "analysis"
            continue
        
        # 根据当前部分添加内容
        if current_section == "chosen":
            temp_chosen.append(line)
        elif current_section == "analysis":
            temp_analysis.append(line)
        else:
            temp_result.append(line)
    
    # 如果有解析出的内容，则使用解析结果
    if temp_chosen:
        chosen_text = "\n".join(temp_chosen)
    if temp_analysis:
        analysis_text = "\n".join(temp_analysis)
    if temp_result:
        result_text = "\n".join(temp_result)
    
    # 如果没有解析出chosen_text和analysis_text，则提供默认值
    if not chosen_text:
        chosen_text = "请咨询专业律师获取具体法律条文引用。"
    if not analysis_text:
        analysis_text = "建议根据具体情况咨询专业法律人士进行详细分析。"
    
    return result_text, chosen_text, analysis_text

@router.put("/getSample/")
async def get_sample():
    """
    获取法律问题示例列表
    """
    try:
        # 返回预定义的法律问题示例
        sample_questions = {
            'questionList': [
                {
                    'text': '我想跟我堂哥结婚，可以吗？'
                },
                {
                    'text': '我现在16岁了，想跟男朋友结婚，可以吗？'
                },
                {
                    'text': '我的老婆以前没有重大疾病，在我们结婚三年之后被诊断为精神病，我现在想跟她离婚，要怎么办理？'
                },
                {
                    'text': '我在公司工作了5年，现在被无故辞退，我可以要求赔偿吗？'
                },
                {
                    'text': '邻居家的狗经常叫，影响我休息，我可以起诉他们吗？'
                },
                {
                    'text': '我借给朋友10万元，现在他不还钱，我该怎么办？'
                }
            ]
        }
        
        return {
            "sample": sample_questions
        }
        
    except Exception as e:
        logging.error(f"getSample接口异常: {e}")
        return {
            "error": f"系统错误: {str(e)}"
        }

@router.put("/chatLegal/")
async def chat_legal(request: ChatLegalRequest):
    """
    法律咨询聊天接口
    """
    try:
        # 检查用户状态
        balance_ok, balance_status = check_user_balance(request.openid)
        if not balance_ok:
            if balance_status == "noUser":
                return {
                    "chatResult": {
                        "status": "noUser"
                    }
                }
            elif balance_status == "runOut":
                return {
                    "chatResult": {
                        "status": "runOut"
                    }
                }
        
        # 检查用户输入
        if not request.userInputStr or request.userInputStr.strip() == "":
            return {
                "chatResult": {
                    "status": "noSessionWord"
                }
            }
        
        # 构建消息
        messages = []
        
        # 添加系统提示
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
            
            # 解析AI响应
            result_text, chosen_text, analysis_text = parse_ai_response(ai_response)
            
            return {
                "chatResult": {
                    "status": "OK",
                    "ResultText": result_text,
                    "chosenText": chosen_text,
                    "analysisText": analysis_text
                }
            }
            
        except Exception as ai_error:
            logging.error(f"AI调用失败: {ai_error}")
            return {
                "chatResult": {
                    "status": "error",
                    "errMsg": f"AI服务暂时不可用: {str(ai_error)}"
                }
            }
    
    except Exception as e:
        logging.error(f"chatLegal接口异常: {e}")
        return {
            "chatResult": {
                "status": "error",
                "errMsg": f"系统错误: {str(e)}"
            }
        }