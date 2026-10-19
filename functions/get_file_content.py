import os

from config import MAX_CHAR_NUM


def get_file_content(working_directory: str, file_path: str) -> str:
    """
        `working_direcotry` is specified by human, `file_path` is for agent
        so agent can read a file flexibly given a limited scope
    """
    try:
        # Validate the path to `file_path` is inside `working_directory`
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))
        is_valid_target_file = os.path.commonpath([abs_working_dir, target_file_path]) == abs_working_dir
        if not is_valid_target_file:
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        # Valid `file_path` exists
        if not os.path.isfile(target_file_path):
            return f'Error: File not found or is not a regular file: {file_path}'
        # Read the file
        with open(target_file_path, "r") as f:
            content = f.read(MAX_CHAR_NUM)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHAR_NUM} characters]'
            return content
    except Exception as e:  # noqa: BLE001
        return f'Error: reading file "{file_path}": {e}'

