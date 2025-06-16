#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用AI聊天接口 -- 基于智谱AI GLM-4-Flash
@Version: 1.0
@Author: lordli
@Date: 2025-06-09
@Description: 提供通用的AI聊天功能，接收消息数组，返回AI响应字符串
"""

import json
from configparser import ConfigParser
from zhipuai import ZhipuAI
from typing import List, Dict, Any

# 从本地ini中读取默认配置
config = ConfigParser()
config.read(r'config.ini', encoding='utf-8')

class CommonAIChat:
    """
    通用AI聊天类
    """
    
    def __init__(self, model='glm-4-flash', temperature=0.7, max_tokens=1000):
        """
        初始化AI聊天客户端
        
        Args:
            model (str): 使用的模型名称，默认为 'glm-4-flash'
            temperature (float): 温度参数，控制回答的随机性，默认为 0.7
            max_tokens (int): 最大token数量，默认为 1000
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        try:
            self.client = ZhipuAI(
                api_key=config.get('zhipu', 'zhipu_api_key')
            )
        except Exception as e:
            raise Exception(f"初始化ZhipuAI客户端失败: {e}")
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        发送消息到AI并获取响应
        
        Args:
            messages (List[Dict[str, str]]): 消息列表，每个消息包含 'role' 和 'content' 字段
                例如: [
                    {"role": "system", "content": "你是一个有用的助手"},
                    {"role": "user", "content": "你好"}
                ]
        
        Returns:
            str: AI的响应内容
        
        Raises:
            ValueError: 当输入参数无效时
            Exception: 当API调用失败时
        """
        
        # 验证输入参数
        if not isinstance(messages, list) or len(messages) == 0:
            raise ValueError("messages必须是非空的列表")
        
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError("每个消息必须包含 'role' 和 'content' 字段")
            
            if msg['role'] not in ['system', 'user', 'assistant']:
                raise ValueError("role必须是 'system', 'user' 或 'assistant'")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            
            if response and response.choices and len(response.choices) > 0:
                result = response.choices[0].message.content
                return result
            else:
                raise Exception("AI响应为空或格式异常")
                
        except Exception as e:
            raise Exception(f"调用AI接口失败: {e}")


def chat_with_ai(messages: List[Dict[str, str]], 
                 model: str = 'glm-4-flash', 
                 temperature: float = 0.7, 
                 max_tokens: int = 1000) -> str:
    """
    便捷函数：直接调用AI聊天接口
    
    Args:
        messages (List[Dict[str, str]]): 消息列表
        model (str): 模型名称
        temperature (float): 温度参数
        max_tokens (int): 最大token数量
    
    Returns:
        str: AI响应内容
    """
    ai_chat = CommonAIChat(model=model, temperature=temperature, max_tokens=max_tokens)
    return ai_chat.chat(messages)


if __name__ == "__main__":
    # 测试示例
    test_messages = [
        {"role": "system", "content": "请基于我给出的股票概念板块的中文名，生成全大写的不含空格的英文简称，要尽可能的短"},
        {"role": "user", "content": "新能源汽车"},
        {"role": "assistant", "content": "NEV"},
        {"role": "user", "content": "白酒"}
    ]
    
    try:
        result = chat_with_ai(test_messages, temperature=0, max_tokens=50)
        print(f"AI响应: {result}")
    except Exception as e:
        print(f"测试失败: {e}")