"""The Mirascope OpenAI Module."""

from typing import TypeAlias
from wave import Wave_read

from openai.types.chat import ChatCompletionMessageParam

from ..base import BaseMessageParam
from ..base.types import AudioSegment
from ._call import openai_call
from ._call import openai_call as call
from .call_params import OpenAICallParams
from .call_response import OpenAICallResponse
from .call_response_chunk import OpenAICallResponseChunk
from .dynamic_config import OpenAIDynamicConfig
from .stream import OpenAIStream
from .tool import OpenAITool, OpenAIToolConfig

OpenAIMessageParam: TypeAlias = (
    ChatCompletionMessageParam | BaseMessageParam | AudioSegment | Wave_read
)

__all__ = [
    "call",
    "OpenAIDynamicConfig",
    "OpenAICallParams",
    "OpenAICallResponse",
    "OpenAICallResponseChunk",
    "OpenAIMessageParam",
    "OpenAIStream",
    "OpenAITool",
    "OpenAIToolConfig",
    "openai_call",
]
