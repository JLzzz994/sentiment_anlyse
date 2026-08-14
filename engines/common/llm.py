import asyncio
from typing import TypeVar, Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage

from pydantic import BaseModel, Field

from engines.common.retries import with_retry
from engines.contracts.agent_roles import ROLE_INFOS, RoleKey
from engines.contracts.settings import get_settings

T = TypeVar('T', bound=BaseModel)  # 需要类型继承BaseModel


class LLMClient:
    """
    LLM client class客户端
    """

    def __init__(self, model_name: str, model_provider: str, api_key: str, base_url: str):
        self._model_name = model_name
        self._model_provider = model_provider
        self._api_key = api_key
        self._base_url = base_url

    @classmethod
    def from_role(cls, role: RoleKey) -> 'LLMClient':
        """
        根据agent的角色获取到llm_client
        :param role:
        :return:
        """
        role_info = ROLE_INFOS[role]
        config_prefix = role_info.config_prefix
        settings = get_settings()
        return cls(
            model_name=getattr(settings, config_prefix + 'MODEL_NAME'),
            model_provider=getattr(settings, config_prefix + 'MODEL_PROVIDER'),
            api_key=getattr(settings, config_prefix + 'API_KEY'),
            base_url=getattr(settings, config_prefix + 'BASE_URL'),
        )

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        """
        返回llm的文本消息内容
        :param system_prompt:
        :param user_prompt:
        :return:
        """

        # 1.  实例化llm_client
        llm_client = self._build_chat_model(is_structured=False)
        # 2. 调用ainvoke
        messages = self._build_input(system_prompt, user_prompt)
        final_chunks = []
        async for chunk in llm_client.astream(messages):
            if text := chunk.text:
                final_chunks.append(text)
        # 3. 返回
        return ''.join(final_chunks)

    @with_retry
    async def generate_object(self, system_prompt: str, user_prompt: str, output_model: type[T]) -> T:
        """
        返回Pydantic处理后的结构化对象
        :param system_prompt:
        :param user_prompt:
        :param output_model:模型输出的类型
        :return:
        """
        llm_client = self._build_chat_model()

        # 2. 调用xxx 输出方法 method:json_mode(最弱) json_schema(最强) 物理层面 function_calling(支持性最好的) 训练出来的格式 tool_call:是function_calling升级后的
        structured_output = llm_client.with_structured_output(output_model, method="function_calling")  # 100%输出结构化对象
        messages = self._build_input(system_prompt, user_prompt)
        result = await structured_output.ainvoke(messages)
        # 3. 返回
        if result is None:
            raise ValueError(f"{self._model_name}LLM输出结果为空")
        return result

    def _build_chat_model(self, is_structured: bool = True):
        model_name = self._model_name.lower()
        kwargs: dict[str, Any] = {}
        if is_structured and ('kimi' in model_name or 'moonshot' in model_name):
            kwargs['extra_body'] = {
                "thinking": {
                    "type": "disabled"
                }
            }
        return init_chat_model(
            model=self._model_name,
            model_provider=self._model_provider,
            api_key=self._api_key,
            base_url=self._base_url,
            **kwargs
        )

    def _build_input(self, system_prompt: str, user_prompt: str) -> list[BaseMessage]:
        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]






