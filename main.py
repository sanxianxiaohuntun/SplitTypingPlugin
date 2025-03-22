from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import NormalMessageResponded, PersonNormalMessageReceived, GroupNormalMessageReceived
from pkg.platform.types.message import MessageChain, Plain
import yaml
import os
import asyncio
import re
import time


# 注册插件
@register(name="SplitTypingPlugin", description="模拟人类打字习惯的消息分段发送插件", version="0.1", author="小馄饨")
class DelayedResponsePlugin(BasePlugin):
    # 默认配置
    default_config = {
        # 每个字符的延迟时间(秒)
        "delay_per_char": 0.5,
        # 允许分段功能
        "enable_split": True,
        # 需要保留的标点符号
        "keep_punctuation": ["？", "！", "?", "!", "~", "〜"],
        # 需要删除的标点符号
        "skip_punctuation": ["，", "。", ",", ".", ":", "：", "\n"],
        # 作为分段标记的标点符号
        "split_punctuation": ["？", "！", "?", "!", "〜"]
    }
    
    # 插件加载时触发
    def __init__(self, host: APIHost):
        super().__init__(host)
        self.config = self.default_config.copy()
        self.config_file = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.load_config()
        
    # 加载配置
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                if config:
                    self.config.update(config)
                    self.host.ap.logger.info(f"插件已加载配置：{self.config}")
            except Exception as e:
                self.host.ap.logger.error(f"插件加载配置失败：{e}")
        else:
            # 创建默认配置文件
            self.save_config()
            
    # 保存配置
    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, allow_unicode=True)
            self.host.ap.logger.info("插件已保存配置")
        except Exception as e:
            self.host.ap.logger.error(f"插件保存配置失败：{e}")
    
    # 异步初始化
    async def initialize(self):
        self.host.ap.logger.info("插件已初始化")
        
    # 智能分段文本
    def split_text(self, text: str) -> list:
        # 如果不启用分段，直接返回原文本
        if not self.config.get("enable_split", True):
            return [text]
            
        # 先处理括号内的内容
        segments = []
        current = ""
        in_parentheses = False
        
        # 需要删除的标点符号
        skip_punctuation = self.config.get("skip_punctuation", ["，", "。", ",", ".", ":", "：", "\n"])
        # 作为分段标记的标点符号
        split_punctuation = self.config.get("split_punctuation", ["？", "！", "?", "!"])
        
        for i, char in enumerate(text):
            if char == '(':
                in_parentheses = True
                if current.strip():
                    segments.append(current.strip())
                current = char
            elif char == ')':
                in_parentheses = False
                current += char
                segments.append(current.strip())
                current = ""
            elif char in skip_punctuation and not in_parentheses:
                continue
            else:
                current += char
                # 如果不在括号内且遇到分隔符，进行分段
                if not in_parentheses and char in split_punctuation:
                    segments.append(current.strip())
                    current = ""
        
        # 处理最后剩余的文本
        if current.strip():
            segments.append(current.strip())
        
        return [seg for seg in segments if seg.strip()]
    
    # 处理私聊消息命令
    @handler(PersonNormalMessageReceived)
    async def on_person_message_received(self, ctx: EventContext):
        await self.process_command(ctx)
    
    # 处理群聊消息命令
    @handler(GroupNormalMessageReceived)
    async def on_group_message_received(self, ctx: EventContext):
        await self.process_command(ctx)
        
    # 处理命令
    async def process_command(self, ctx: EventContext):
        # 获取消息文本
        message = ctx.event.text_message.strip()
        
        # 处理开启/关闭分段命令
        if message == "/开启分段":
            self.config["enable_split"] = True
            self.save_config()
            
            # 回复用户
            response = "已开启消息分段发送功能"
            ctx.add_return("reply", [response])
            ctx.prevent_default()
            
            self.host.ap.logger.info("已开启分段功能")
            
        elif message == "/关闭分段":
            self.config["enable_split"] = False
            self.save_config()
            
            # 回复用户
            response = "已关闭消息分段发送功能"
            ctx.add_return("reply", [response])
            ctx.prevent_default()
            
            self.host.ap.logger.info("已关闭分段功能")
    
    # 当AI回复消息时触发
    @handler(NormalMessageResponded)
    async def on_normal_message_responded(self, ctx: EventContext):
        # 获取回复消息
        response_text = ctx.event.response_text
        
        # 如果没有回复消息，不处理
        if not response_text:
            return
        
        # 记录原始回复
        self.host.ap.logger.debug(f"DelayedResponse插件拦截到原始回复: {response_text}")
        
        # 智能分段
        segments = self.split_text(response_text)
        self.host.ap.logger.debug(f"DelayedResponse插件分段结果: {segments}")
        
        # 如果没有分段，或者只有一个分段，不进行特殊处理
        if not segments or len(segments) == 1:
            return
        
        # 阻止默认行为
        ctx.prevent_default()
        
        # 获取每个字符的延迟时间
        delay_per_char = self.config.get("delay_per_char", 0.5)
        
        # 按顺序发送每个分段
        for segment in segments:
            # 创建消息链
            message_chain = MessageChain([Plain(segment)])
            
            # 发送消息
            await ctx.reply(message_chain)
            
            # 根据分段长度计算延迟时间
            delay_time = len(segment) * delay_per_char
            await asyncio.sleep(delay_time)
        
    # 插件卸载时触发
    def __del__(self):
        pass
