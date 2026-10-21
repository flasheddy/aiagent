"""AI code-assistance CLI.

The module is split into a pure core and a few explicit effect boundaries:

* pure functions derive values (argument parsing, message building, response
  validation, rendering). They take all their inputs as arguments and return
  new values without touching the environment, the network, or stdout.
* effect boundaries do exactly one impure thing each: read the environment,
  construct the API client, perform the chat completion, execute tool calls,
  and print.

``main`` is the composition root that wires those pieces together, so the
program's behaviour is observable from a single place.
"""

import argparse
import os
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessage,
    ChatCompletionMessageFunctionToolCall,
)

from functions.call_function import available_functions, call_function
from prompts import system_prompt

MODEL = "openrouter/free"
BASE_URL = "https://openrouter.ai/api/v1"
API_KEY_ENV = "OPENROUTER_API_KEY"
MAX_ITERATIONS = 20

# Injected effect: executes one tool call and returns a tool message.
ToolExecutor = Callable[[ChatCompletionMessageFunctionToolCall, bool], dict[str, str]]


@dataclass(frozen=True)
class CliArgs:
    """Parsed command-line arguments."""

    user_prompt: str
    verbose: bool


@dataclass(frozen=True)
class TokenUsage:
    """Token accounting for one completion."""

    prompt_tokens: int
    completion_tokens: int


# --------------------------------------------------------------------------
# Pure core
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Code Assistance")
    _ = parser.add_argument("user_prompt", type=str, help="Prompt to send to the LLM")
    # add verbose argument
    _ = parser.add_argument(
        "--verbose", action="store_true", help="Show the token usage report"
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> CliArgs:
    """Turn raw argv into a validated value object."""
    args = build_parser().parse_args(argv)
    return CliArgs(
        user_prompt=cast(str, args.user_prompt),
        verbose=cast(bool, args.verbose),
    )


def require_api_key(environ: Mapping[str, str]) -> str:
    """Extract the API key from a mapping, or fail with an actionable error."""
    api_key = environ.get(API_KEY_ENV)
    if not api_key:
        raise RuntimeError("Please configure the right api_key")
    return api_key


def build_messages(user_prompt: str) -> list[ChatCompletionMessage]:
    """Compose the conversation seeded with the system prompt."""
    return [  # pyright: ignore[reportReturnType]
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def get_token_usage(response: ChatCompletion) -> TokenUsage:
    if not response.usage:
        raise RuntimeError("The API response token usage appears to be malformed")
    return TokenUsage(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )


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


def get_tool_calls_result(
    message: ChatCompletionMessage,
    verbose: bool = False,
    execute: ToolExecutor = call_function,
) -> list[dict[str, str]] | str:
    """Return the assistant's answer, executing any requested tool calls.

    The tool executor is injected so callers can substitute the effect without
    changing this function's contract.
    """
    tool_calls = message.tool_calls
    if not tool_calls:
        return get_content(message)
    tool_messages = [
        execute(tool_call, verbose)
        for tool_call in tool_calls
        if tool_call.type == "function"
    ]
    return tool_messages


def format_verbose_report(cli: CliArgs, usage: TokenUsage, response_text: str) -> str:
    """Build the verbose report as a single string."""
    return (
        f"User prompt: {cli.user_prompt}\n"
        f"Prompt tokens: {usage.prompt_tokens}\n"
        f"Response tokens: {usage.completion_tokens}\n"
        f"Response:\n{response_text}"
    )


# --------------------------------------------------------------------------
# Effect boundaries
# --------------------------------------------------------------------------


def load_api_key() -> str:
    """Load .env into the process environment and read the key."""
    _ = load_dotenv()
    return require_api_key(os.environ)


def create_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=BASE_URL, api_key=api_key)


def get_response(client: OpenAI, messages: list[dict[str, str]]) -> ChatCompletion:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,  # pyright: ignore[reportArgumentType]
        tools=available_functions,  # pyright: ignore[reportArgumentType]
    )
    if not response:
        raise RuntimeError("Failed to make a request")
    return response


# --------------------------------------------------------------------------
# Composition root
# --------------------------------------------------------------------------


def main(argv: Sequence[str] | None = None) -> None:
    cli = parse_args(argv)
    client = create_client(load_api_key())
    messages = build_messages(cli.user_prompt)
    # Agentic Loop
    for _ in range(MAX_ITERATIONS):
        response = get_response(client, messages)  # pyright: ignore[reportArgumentType]
        msg = get_message(response)
        messages.append(msg)
        tool_call_result: list[dict[str, str]] | str = get_tool_calls_result(
            msg, cli.verbose
        )
        if isinstance(tool_call_result, list):
            messages.extend(tool_call_result)  # pyright: ignore[reportArgumentType]
        else:
            print(
                format_verbose_report(cli, get_token_usage(response), tool_call_result)
                if cli.verbose
                else tool_call_result
            )
            return

    print(f"Reached the maximum number of {MAX_ITERATIONS} iterations")
    sys.exit(1)


if __name__ == "__main__":
    main()
