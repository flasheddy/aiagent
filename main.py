import argparse
import json
import os
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessage

from functions.call_function import available_functions
from prompts import system_prompt


def main():
    # Get API key
    _ = load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Please configure the right api_key")

    # Initiate a client
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    # Parse user argument
    parser = argparse.ArgumentParser(description="AI Code Assistance")
    _ = parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    # add verbose argument
    _ = parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    args = parser.parse_args()
    user_prompt = cast(str, args.user_prompt)  # args.user_prompt is Any
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    res = get_response(client, messages)
    if cast(bool, args.verbose):
        prompt_token_num, completion_token_num = get_token_usage(res)
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {prompt_token_num}")
        print(f"Response tokens: {completion_token_num}")
    print(f"Response:\n{get_tool_calls(get_message(res))}")


def get_response(client: OpenAI, messages: list[dict[str, str]]) -> ChatCompletion:
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,  # pyright: ignore[reportArgumentType]
        tools=available_functions,  # pyright: ignore[reportArgumentType]
    )
    if not response:
        raise RuntimeError("Failed to make a request")
    return response


def get_token_usage(response: ChatCompletion) -> tuple[int, int]:
    if not response.usage:
        raise RuntimeError("The API response token usage appears to be malformed")
    return response.usage.prompt_tokens, response.usage.completion_tokens


def get_message(response: ChatCompletion) -> ChatCompletionMessage:
    msg = response.choices[0].message
    if not msg:
        raise RuntimeError("The API response message appears to be malformed")
    return msg


def get_content(message: ChatCompletionMessage) -> str:
    content = message.content
    if not content:
        raise RuntimeError("The API response message content appears to be malformed")
    return content


def get_tool_calls(message: ChatCompletionMessage) -> str:
    tool_calls = message.tool_calls
    if not tool_calls:
        return get_content(message)
    function_dict = {
        tool_call.function.name: json.loads(tool_call.function.arguments or "{}")
        for tool_call in tool_calls
        if tool_call.type == "function"
    }
    lines = [
        f"Calling function: {func_name}({func_args})"
        for func_name, func_args in function_dict.items()  # pyright: ignore[reportAny]
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
