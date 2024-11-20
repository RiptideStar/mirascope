"""This module contains the setup_call function for Mistral tools."""

from collections.abc import (
    Awaitable,
    Callable,
)
from typing import Any, cast, overload

from mistralai import Mistral
from mistralai.models import (
    AssistantMessage,
    ChatCompletionResponse,
    CompletionEvent,
    ResponseFormat,
    SystemMessage,
    TextChunk,
    ToolChoiceEnum,
    ToolMessage,
    UserMessage,
)

from ... import BaseMessageParam, mistral
from ...base import BaseTool, _utils
from ...base._utils import (
    AsyncCreateFn,
    CreateFn,
    fn_is_async,
    get_async_create_fn,
    get_create_fn,
)
from ...base.call_params import CommonCallParams
from .._call_kwargs import MistralCallKwargs
from ..call_params import MistralCallParams
from ..dynamic_config import MistralDynamicConfig
from ..tool import MistralTool
from ._convert_common_call_params import convert_common_call_params
from ._convert_message_params import convert_message_params


@overload
def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams | CommonCallParams,
    extract: bool,
    stream: bool,
) -> tuple[
    AsyncCreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


@overload
def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., MistralDynamicConfig],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams | CommonCallParams,
    extract: bool,
    stream: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]: ...


def setup_call(
    *,
    model: str,
    client: Mistral | None,
    fn: Callable[..., MistralDynamicConfig | Awaitable[MistralDynamicConfig]],
    fn_args: dict[str, Any],
    dynamic_config: MistralDynamicConfig,
    tools: list[type[BaseTool] | Callable] | None,
    json_mode: bool,
    call_params: MistralCallParams | CommonCallParams,
    extract: bool,
    stream: bool,
) -> tuple[
    CreateFn[ChatCompletionResponse, CompletionEvent]
    | AsyncCreateFn[ChatCompletionResponse, CompletionEvent],
    str | None,
    list[AssistantMessage | SystemMessage | ToolMessage | UserMessage],
    list[type[MistralTool]] | None,
    MistralCallKwargs,
]:
    prompt_template, messages, tool_types, base_call_kwargs = _utils.setup_call(
        fn,
        fn_args,
        dynamic_config,
        tools,
        MistralTool,
        call_params,
        convert_common_call_params,
    )
    call_kwargs = cast(MistralCallKwargs, base_call_kwargs)
    messages = cast(
        list[
            BaseMessageParam
            | AssistantMessage
            | SystemMessage
            | ToolMessage
            | UserMessage
        ],
        messages,
    )
    messages = convert_message_params(messages)
    if json_mode:
        call_kwargs["response_format"] = ResponseFormat(type="json_object")
        json_mode_content = _utils.json_mode_content(
            tool_types[0] if tool_types else None
        )
        if messages[-1].role == "user":
            if isinstance(messages[-1].content, list):
                messages[-1].content.append(TextChunk(text=json_mode_content))
            elif isinstance(messages[-1].content, str):
                messages[-1].content += json_mode_content
        else:
            messages.append(UserMessage(content=json_mode_content.strip()))
        call_kwargs.pop("tools", None)
    elif extract:
        assert tool_types, "At least one tool must be provided for extraction."
        call_kwargs["tool_choice"] = cast(ToolChoiceEnum, "any")
    call_kwargs |= {"model": model, "messages": messages}

    if client is None:
        client = Mistral(api_key=mistral.load_api_key())
    if fn_is_async(fn):
        create_or_stream = get_async_create_fn(
            client.chat.complete_async, client.chat.stream_async
        )
    else:
        create_or_stream = get_create_fn(client.chat.complete, client.chat.stream)
    return create_or_stream, prompt_template, messages, tool_types, call_kwargs
