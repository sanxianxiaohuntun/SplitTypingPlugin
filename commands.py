from typing import cast, AsyncGenerator

from .main import DelayedResponsePlugin
from pkg.command.errors import CommandError
from pkg.command.operator import operator_class, CommandOperator
from pkg.command.entities import ExecuteContext, CommandReturn


def get_split_plugin(self) -> DelayedResponsePlugin:
    return cast(
        DelayedResponsePlugin,
        self.ap.plugin_mgr.get_plugin(
            plugin_name="SplitTypingPlugin",
            author="小馄饨"
        ).plugin_inst
    )


# 处理开启分段命令
@operator_class(
    name="开启分段",
    help="开启分段发送功能",
    usage="!开启分段"
)
class EnableSplitCommand(CommandOperator):
    async def execute(self, ctx: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        # 获取插件
        plugin = get_split_plugin(self)

        plugin.config["enable_split"] = True
        plugin.save_config()

        self.ap.logger.info("已开启分段功能")

        # 回复用户
        response = "已开启消息分段发送功能"
        yield CommandReturn(text=response)


# 处理关闭分段命令
@operator_class(
    name="关闭分段",
    help="关闭分段发送功能",
    usage="!关闭分段"
)
class DisableSplitCommand(CommandOperator):
    async def execute(self, ctx: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        # 获取插件
        plugin = get_split_plugin(self)

        plugin.config["enable_split"] = False
        plugin.save_config()

        self.ap.logger.info("已关闭分段功能")

        # 回复用户
        response = "已关闭消息分段发送功能"
        yield CommandReturn(text=response)

# 处理显示推理过程命令
@operator_class(
    name="显示推理",
    help="关闭推理过程隐藏功能",
    usage="!显示推理"
)
class DisableHideReasoningContent(CommandOperator):
    async def execute(self, ctx: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        # 获取插件
        plugin = get_split_plugin(self)

        plugin.config["hide_reasoning_content"] = False
        plugin.save_config()

        self.ap.logger.info("已关闭推理过程隐藏功能")

        # 回复用户
        response = "已关闭推理过程隐藏功能"
        yield CommandReturn(text=response)


# 处理隐藏推理过程命令
@operator_class(
    name="隐藏推理",
    help="开启推理内容隐藏功能",
    usage="!隐藏推理"
)
class EnableHideReasoningContent(CommandOperator):
    async def execute(self, ctx: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        # 获取插件
        plugin = get_split_plugin(self)

        plugin.config["hide_reasoning_content"] = True
        plugin.save_config()

        self.ap.logger.info("已开启推理内容隐藏功能")

        # 回复用户
        response = "已开启推理内容隐藏功能"
        yield CommandReturn(text=response)


# 处理隐藏推理过程命令
@operator_class(
    name="设置分段字符限制",
    help="设置分段字符限制",
    usage="!设置分段字符限制 [字符数限制]"
)
class SetSplitLimitCommand(CommandOperator):
    async def execute(self, ctx: ExecuteContext) -> AsyncGenerator[CommandReturn, None]:
        # 如果参数数量不为1
        if len(ctx.crt_params) != 1:
            yield CommandReturn(error=CommandError("请输入正确的数字格式，例如：!设置分段字符限制 100"))
            return

        #如果参数不是非负整数
        if not ctx.crt_params[0].isdigit():
            yield CommandReturn(error=CommandError("请输入正确的数字格式，例如：!设置分段字符限制 100"))
            return

        # 将限制转化为int型
        limit = int(ctx.crt_params[0])

        # 获取插件
        plugin = get_split_plugin(self)

        plugin.config["max_chars_for_split"] = limit
        plugin.save_config()

        self.ap.logger.info(f"已设置分段字符限制为 {limit}")

        # 回复用户
        if limit > 0:
            response = f"已设置：超过 {limit} 个字符的消息将不会分段"
        else:
            response = "已设置：不限制字符数，所有消息都可能分段"

        yield CommandReturn(text=response)
