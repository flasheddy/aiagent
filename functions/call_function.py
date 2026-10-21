import json
from collections.abc import Callable, Mapping
from typing import cast

from openai.types.chat import ChatCompletionMessageFunctionToolCall

from config import WORKING_DIR
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import schema_write_file, write_file

available_functions = [
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
]

# Define a mapping of function names to actual functions
function_map: dict[str, Callable[..., str]] = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def parse_arguments(raw_arguments: str | None) -> dict[str, object] | None:
    """Decode tool arguments into a keyword mapping.

    Returns ``None`` when the payload is valid JSON but not an object; malformed
    JSON propagates as ``json.JSONDecodeError`` so the caller can report it.
    """
    parsed = cast(object, json.loads(raw_arguments or "{}"))
    if not isinstance(parsed, dict):
        return None
    return cast(dict[str, object], parsed)


def format_call_log(
    function_name: str, function_args: Mapping[str, object]
) -> str:
    """Render the verbose call line; performs no I/O."""
    return f" - Calling function: {function_name}({dict(function_args)})"


def tool_message(tool_call_id: str, content: str) -> dict[str, str]:
    """Build a tool result message in the shape the chat API expects."""
    return {"role": "tool", "tool_call_id": tool_call_id, "content": content}


def call_function(
    tool_call: ChatCompletionMessageFunctionToolCall, verbose: bool = False
) -> dict[str, str]:
    """Execute one tool call and return the tool message.

    Side effects are limited to one optional log line (``verbose``) and the tool
    invocation itself. Invalid model output is reported as an error message
    rather than raised, so one bad call cannot abort the conversation.
    """
    function_name = tool_call.function.name
    try:
        function_args = parse_arguments(tool_call.function.arguments)
    except json.JSONDecodeError as exc:
        return tool_message(
            tool_call.id,
            f"Error: arguments for {function_name} are not valid JSON: {exc}",
        )
    if function_args is None:
        return tool_message(
            tool_call.id,
            f"Error: arguments for {function_name} must be a JSON object",
        )
    # Guard an unknown function
    if function_name not in function_map:
        return tool_message(tool_call.id, f"Error: Unknown function: {function_name}")
    if verbose:
        print(format_call_log(function_name, function_args))
    try:
        # Inject the working directory for the agent to work; the model cannot
        # override it because the injection is applied last.
        result = function_map[function_name](
            **{**function_args, "working_directory": WORKING_DIR}
        )
    except Exception as exc:  # noqa: BLE001
        return tool_message(tool_call.id, f"Error: {function_name} failed: {exc}")
    return tool_message(tool_call.id, result)
